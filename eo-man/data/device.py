from eltakobus.device import SensorInfo, KeyFunction
from eltakobus.util import b2s, AddressExpression
from eltakobus.device import BusObject, FAM14
from eltakobus.message import *
from eltakobus.eep import *

from data.homeassistant_const import CONF_ID, CONF_DEVICE, CONF_DEVICES, CONF_NAME, CONF_PLATFORM, CONF_TYPE, CONF_DEVICE_CLASS, CONF_TEMPERATURE_UNIT, UnitOfTemperature, Platform

from data.data_helper import *
from data.const import *

class Device():
    """Data representation of a device"""
    static_info:dict={}
    address:str = None
    channel:int=None
    dev_size:int=None
    external_id:str=None
    device_type:str=None
    key_function:str=None
    version:str=None
    name:str=None
    comment:str = ""
    base_id:str=None
    bus_device:bool=False
    memory_entries:[SensorInfo]=[]  # only used for bus devices

    # vars for ha
    use_in_ha:bool=False
    ha_platform:Platform=None
    eep:str=None
    additional_fields:dict={}


    def __init__(self, 
                 address:str=None, 
                 bus_device:bool=False,
                 dev_size:int=1,
                 channel:int=1, 
                 external_id:str=None, 
                 device_type:str=None, 
                 version:str=None, 
                 name:str=None, 
                 comment:str=None, 
                 base_id:str=None, 
                 memory_entries:[SensorInfo]=[]):
        
        self.address = address
        self.bus_device = bus_device
        self.channel = channel
        self.dev_size = dev_size
        self.external_id = external_id
        self.device_type = device_type
        self.version = version
        self.name = name
        self.comment = comment
        self.base_id = base_id
        self.memory_entries = memory_entries

    def is_fam14(self) -> bool:
        return self.external_id == self.base_id
    
    def is_bus_device(self) -> bool:
        return self.bus_device
        # return self.address.startswith('00-00-00-')            

    @classmethod
    async def async_get_bus_device_by_natvice_bus_object(cls, device: BusObject, fam14: FAM14, channel:int=1):

        bd = Device()
        bd.additional_fields = {}
        id = device.address + channel -1
        bd.address = a2s( id )
        bd.channel = channel
        bd.dev_size = device.size
        bd.base_id = await fam14.get_base_id()
        bd.device_type = type(device).__name__
        bd.version = '.'.join(map(str,device.version))
        bd.key_function = ''
        bd.comment = ''
        bd.bus_device = True
        if isinstance(device, FAM14):
            bd.external_id = bd.base_id
            bd.use_in_ha = True
        else:
            bd.external_id = a2s( (await fam14.get_base_id_in_int()) + id )
        bd.memory_entries = [m for m in (await device.get_all_sensors()) if b2s(m.dev_adr) == bd.address]
        # print(f"{bd.device_type} {bd.address}")
        # print_memory_entires( bd.memory_entries)
        # print("\n")
        bd.name = f"{bd.device_type} {bd.address}"
        if bd.is_fam14():
            bd.name = f"{bd.device_type} {bd.external_id}"
        if bd.dev_size > 1:
            bd.name += f" ({bd.channel}/{bd.dev_size})"

        info:dict = find_device_info_by_device_type(bd.device_type)
        if info is not None:
            bd.use_in_ha = True
            bd.ha_platform = info[CONF_TYPE]
            bd.eep = info.get(CONF_EEP, None)

            if info.get('sender_eep', None):
                bd.additional_fields['sender'] = {
                    CONF_ID: a2s( SENDER_BASE_ID + id ),
                    CONF_EEP: info.get('sender_eep')
                }

            if info[CONF_TYPE] == Platform.COVER:
                bd.additional_fields[CONF_DEVICE_CLASS] = 'shutter'
                bd.additional_fields[CONF_TIME_CLOSES] = 25
                bd.additional_fields[CONF_TIME_OPENS] = 25

            if info[CONF_TYPE] == Platform.CLIMATE:
                bd.additional_fields[CONF_TEMPERATURE_UNIT] = f"'{UnitOfTemperature.KELVIN}'"
                bd.additional_fields[CONF_MIN_TARGET_TEMPERATURE] = 16
                bd.additional_fields[CONF_MAX_TARGET_TEMPERATURE] = 25
                thermostat = BusObjectHelper.find_sensor(bd.memory_entries, device.address, channel, in_func_group=1)
                if thermostat:
                    bd.additional_fields[CONF_ROOM_THERMOSTAT] = {}
                    bd.additional_fields[CONF_ROOM_THERMOSTAT][CONF_ID] = b2s(thermostat.sensor_id)
                    bd.additional_fields[CONF_ROOM_THERMOSTAT][CONF_EEP] = A5_10_06.eep_string   #TODO: derive EEP from switch/sensor function
                #TODO: cooling_mode

        return bd
    
    @classmethod
    def get_decentralized_device_by_telegram(cls, msg: RPSMessage):
        bd = Device()
        bd.address = b2s( msg.address )
        bd.base_id = '00-00-00-00'
        bd.device_type = 'unknown'
        bd.version = 'unknown'
        bd.comment = ''
        if int.from_bytes( msg.address, "big") > 0x0000FFFF:
            bd.external_id = b2s( msg.address )
        else:
            bd.external_id = 'unknown'
        bd.name = 'unknown'
        return bd
    
    @classmethod
    async def async_get_decentralized_device_by_sensor_info(cls, sensor_info:SensorInfo, device: BusObject, fam14: FAM14, channel:int=1):
        bd = Device()
        bd.address = sensor_info.sensor_id_str
        bd.base_id = await fam14.get_base_id()
        bd.comment = ''
        bd.key_function = KeyFunction(sensor_info.key_func).name
        bd.eep = get_eep_from_key_function_name(sensor_info.key_func)
        bd.name = f"{get_name_from_key_function_name(sensor_info.key_func)} {sensor_info.sensor_id_str}"
        # found sensor by EEP in KeyFunction
        if bd.eep and bd.name:
            bd.use_in_ha = True
            bd.device_type = 'Sensor'
            bd.ha_platform = Platform.SENSOR
        # buttons but ignore virtual buttons from HA
        elif 'PUSH_BUTTON' in KeyFunction(sensor_info.key_func).name and not sensor_info.sensor_id_str.startswith('00-00-'):
            bd.use_in_ha = True
            bd.device_type = 'Button'
            bd.ha_platform = Platform.BINARY_SENSOR
            bd.eep = F6_02_01.eep_string
            bd.name = f"Button {sensor_info.sensor_id_str}"
        # is from FTS14EM
        elif int.from_bytes(sensor_info.sensor_id, "big") < 0x1500:
            bd.use_in_ha = True
            bd.device_type = 'FTS14EM Button'
            bd.ha_platform = Platform.BINARY_SENSOR
            bd.eep = F6_02_01.eep_string
            bd.name = 'FTS14EM Button ' + sensor_info.sensor_id_str
        elif bd.address.startswith('00-00-B') or 'FROM_CONTROLLER' in bd.key_function:
            bd.use_in_ha = False
            bd.device_type = 'Smart Home'
            bd.ha_platform = ''
            bd.eep = ''
            bd.name = 'HA Contoller ' + sensor_info.sensor_id_str
        elif 'WEATHER_STATION' in bd.key_function:
            bd.use_in_ha = True
            bd.device_type = 'Weather Station'
            bd.ha_platform = Platform.SENSOR
            bd.eep = 'A5-04-02'
            bd.name = 'Weather Station ' + sensor_info.sensor_id_str

        if sensor_info.sensor_id_str.startswith('00-00-'):
            bd.external_id = a2s( int.from_bytes(sensor_info.sensor_id, "big") + (await fam14.get_base_id_in_int()) )
        else:
            bd.external_id = sensor_info.sensor_id_str
        bd.version = 'unknown'
        return bd