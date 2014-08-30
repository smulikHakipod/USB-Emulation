
import socket
import struct
import types

class BaseStucture:
    def __init__(self, **kwargs):
        self.init_from_dict(**kwargs)
        for field in self._fields_:
            if len(field) > 2:
                if not hasattr(self, field[0]):
                    setattr(self, field[0], field[2])

    def init_from_dict(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def size(self):
        return struct.calcsize(self.format())

    def format(self):

        pack_format = '>'
        for field in self._fields_:
            if type(field[1]) is types.InstanceType:
                if BaseStucture in field[1].__class__.__bases__:
                    pack_format += str(field[1].size()) + 's'
            elif 'si' == field[1]:
                pack_format += 'c'
            elif '<' in field[1]:
                pack_format += field[1][1:]
            else:
                pack_format += field[1]
        return pack_format

    def pack(self):
        values = []
        for field in self._fields_:
            if type(field[1]) is types.InstanceType:
                if BaseStucture in field[1].__class__.__bases__:
                     values.append(getattr(self, field[0], 0).pack())
            else:
                if 'si' == field[1]:
                    values.append(chr(getattr(self, field[0], 0)))
                else:
                    values.append(getattr(self, field[0], 0))
        return struct.pack(self.format(), *values)


    def unpack(self, buf):
        values = struct.unpack(self.format(), buf)
        i=0
        keys_vals = {}
        for val in values:
            if '<' in self._fields_[i][1][0]:
                val = struct.unpack('<' +self._fields_[i][1][1], struct.pack('>' + self._fields_[i][1][1], val))[0]
            keys_vals[self._fields_[i][0]]=val
            i+=1

        self.init_from_dict(**keys_vals)


def int_to_hex_string(val):
    return str(format(val, 'x')).decode('hex')


class USBIPHeader(BaseStucture):
    _fields_ = [
        ('version', 'H', 262),
        ('command', 'H'),
        ('status', 'I')
    ]



class USBInterface(BaseStucture):
    _fields_ = [
        ('bInterfaceClass', 'B'),
        ('bInterfaceSubClass', 'B'),
        ('bInterfaceProtocol', 'B'),
        ('align', 'B', 0)
    ]


class OPREPDevList(BaseStucture):
    _fields_ = [
        ('base', USBIPHeader()),
        ('nExportedDevice', 'I'),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B'),
        ('interfaces', USBInterface())
    ]



class OPREPImport(BaseStucture):
    _fields_ = [
        ('base', USBIPHeader()),
        ('usbPath', '256s'),
        ('busID', '32s'),
        ('busnum', 'I'),
        ('devnum', 'I'),
        ('speed', 'I'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bConfigurationValue', 'B'),
        ('bNumConfigurations', 'B'),
        ('bNumInterfaces', 'B')
    ]

class USBIPRETSubmit(BaseStucture):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),
        ('status', 'I'),
        ('actual_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('error_count', 'I'),
        ('setup', 'Q')
    ]

    def pack(self):
        packed_data = BaseStucture.pack(self)
        packed_data += self.data
        return packed_data

class USBIPCMDSubmit(BaseStucture):
    _fields_ = [
        ('command', 'I'),
        ('seqnum', 'I'),
        ('devid', 'I'),
        ('direction', 'I'),
        ('ep', 'I'),
        ('transfer_flags', 'I'),
        ('transfer_buffer_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('interval', 'I'),
        ('setup', 'Q')
    ]

class USBIPUnlinkReq(BaseStucture):
    _fields_ = [
        ('command', 'I', 0x2),
        ('seqnum', 'I'),
        ('devid', 'I', 0x2),
        ('direction', 'I'),
        ('ep', 'I'),
        ('transfer_flags', 'I'),
        ('transfer_buffer_length', 'I'),
        ('start_frame', 'I'),
        ('number_of_packets', 'I'),
        ('interval', 'I'),
        ('setup', 'Q')
    ]




class StandardDeviceRequest(BaseStucture):
    _fields_ = [
        ('bmRequestType', 'B'),
        ('bRequest', 'B'),
        ('wValue', 'H'),
        ('wIndex', 'H'),
        ('wLength', '<H')
    ]

class DeviceDescriptor(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 18),
        ('bDescriptorType', 'B', 1),
        ('bcdUSB', 'H', 0x1001),
        ('bDeviceClass', 'B'),
        ('bDeviceSubClass', 'B'),
        ('bDeviceProtocol', 'B'),
        ('bMaxPacketSize0', 'B'),
        ('idVendor', 'H'),
        ('idProduct', 'H'),
        ('bcdDevice', 'H'),
        ('iManufacturer', 'B'),
        ('iProduct', 'B'),
        ('iSerialNumber', 'B'),
        ('bNumConfigurations', 'B')
    ]


class DeviceConfigurations(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 2),
        ('wTotalLength', 'H', 0x2200),
        ('bNumInterfaces', 'B', 1),
        ('bConfigurationValue', 'B', 1),
        ('iConfiguration', 'B', 0),
        ('bmAttributes', 'B', 0x80),
        ('bMaxPower', 'B', 0x32)
    ]


class InterfaceDescriptor(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 4),
        ('bInterfaceNumber', 'B', 0),
        ('bAlternateSetting', 'B', 0),
        ('bNumEndpoints', 'B', 1),
        ('bInterfaceClass', 'B', 3),
        ('bInterfaceSubClass', 'B', 1),
        ('bInterfaceProtocol', 'B', 2),
        ('iInterface', 'B', 0)
    ]


class EndPoint(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 7),
        ('bDescriptorType', 'B', 0x5),
        ('bEndpointAddress', 'B', 0x81),
        ('bmAttributes', 'B', 0x3),
        ('wMaxPacketSize', 'H', 0x8000),
        ('bInterval', 'B', 0x0A)
    ]



class USBRequest():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class USBDevice():
    '''interfaces = [USBInterface(bInterfaceClass=0x3, bInterfaceSubClass=0x0, bInterfaceProtocol=0x0)]
    speed=2
    speed = 2
    vendorID = 0xc410
    productID = 0x0
    bcdDevice = 0x0
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    bNumConfigurations = 1
    bConfigurationValue = 1
    bNumInterfaces = 1'''

    def __init__(self):
        self.generate_raw_configuration()

    def generate_raw_configuration(self):
        str = self.configurations[0].pack()
        str += self.configurations[0].interfaces[0].pack()
        str += self.configurations[0].interfaces[0].descriptions[0].pack()
        str += self.configurations[0].interfaces[0].endpoints[0].pack()
        self.all_configurations = str

    def send_usb_req(self, usb_req, usb_res, status=0):
        self.connection.sendall(USBIPRETSubmit(command=0x3,
                                                   seqnum=usb_req.seqnum,
                                                   ep=0,
                                                   status=status,
                                                   actual_length=len(usb_res),
                                                   start_frame=0x0,
                                                   number_of_packets=0x0,
                                                   interval=0x0,
                                                   data=usb_res).pack())


    def handle_get_descriptor(self, control_req, usb_req):
        handled = False
        if control_req.wValue == 0x1: # Device
            handled = True
            self.send_usb_req(usb_req, DeviceDescriptor(bDeviceClass=self.bDeviceClass,
                                                        bDeviceSubClass=self.bDeviceSubClass,
                                                        bDeviceProtocol=self.bDeviceProtocol,
                                                        bMaxPacketSize0=0x8,
                                                        idVendor=self.vendorID,
                                                        idProduct=self.productID,
                                                        bcdDevice=self.bcdDevice,
                                                        iManufacturer=0,
                                                        iProduct=0,
                                                        iSerialNumber=0,
                                                        bNumConfigurations=1).pack())
        elif control_req.wValue == 0x2: # configuration
            handled = True
            self.send_usb_req(usb_req, self.all_configurations[:control_req.wLength])

        return handled

    def handle_usb_control(self, usb_req):
        control_req = StandardDeviceRequest()
        control_req.unpack(int_to_hex_string(usb_req.setup))
        handled = False
        if control_req.bmRequestType == 0x80: # Host Request
            if control_req.bRequest == 0x6: # Get Descriptor
                handled = self.handle_get_descriptor(control_req, usb_req)

        if not handled:
            self.handle_unknown_control(control_req, usb_req)

    def handle_usb_request(self, usb_req):
        if usb_req.ep == 0:
            self.handle_usb_control(usb_req)
        else:
            self.handle_data(usb_req)

class USBContainer:
    usb_devices = []

    def add_usb_device(self, usb_device):
        self.usb_devices.append(usb_device)

    def handle_attach(self):
        return OPREPImport(base=USBIPHeader(command=3, status=0),
                           usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1',
                           busID='1-1',
                           busnum=1,
                           devnum=2,
                           speed=2,
                           idVendor=self.usb_devices[0].vendorID,
                           idProduct=self.usb_devices[0].productID,
                           bcdDevice=self.usb_devices[0].bcdDevice,
                           bDeviceClass=self.usb_devices[0].bDeviceClass,
                           bDeviceSubClass=self.usb_devices[0].bDeviceSubClass,
                           bDeviceProtocol=self.usb_devices[0].bDeviceProtocol,
                           bNumConfigurations=self.usb_devices[0].bNumConfigurations,
                           bConfigurationValue=self.usb_devices[0].bConfigurationValue,
                           bNumInterfaces=self.usb_devices[0].bNumInterfaces)

    def handle_device_list(self):
        usb_dev = self.usb_devices[0]
        return OPREPDevList(base=USBIPHeader(command=5,status=0),
                            nExportedDevice=1,
                            usbPath='/sys/devices/pci0000:00/0000:00:01.2/usb1/1-1',
                            busID='1-1',
                            busnum=1,
                            devnum=2,
                            speed=2,
                            idVendor=usb_dev.vendorID,
                            idProduct=usb_dev.productID,
                            bcdDevice=usb_dev.bcdDevice,
                            bDeviceClass=usb_dev.bDeviceClass,
                            bDeviceSubClass=usb_dev.bDeviceSubClass,
                            bDeviceProtocol=usb_dev.bDeviceProtocol,
                            bNumConfigurations=usb_dev.bNumConfigurations,
                            bConfigurationValue=usb_dev.bConfigurationValue,
                            bNumInterfaces=usb_dev.bNumInterfaces,
                            interfaces=USBInterface(bInterfaceClass=usb_dev.configurations[0].interfaces[0].bInterfaceClass,
                                                    bInterfaceSubClass=usb_dev.configurations[0].interfaces[0].bInterfaceSubClass,
                                                    bInterfaceProtocol=usb_dev.configurations[0].interfaces[0].bInterfaceProtocol))


    def run(self, ip='0.0.0.0', port=3240):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((ip, port))
        s.listen(5)
        attached = False
        while 1:
            conn, addr = s.accept()
            print 'Connection address:', addr
            req = USBIPHeader()
            while 1:
                if not attached:
                    data = conn.recv(8)
                    if not data:
                        break
                    req.unpack(data)
                    print 'Header Packet'
                    print 'command:', hex(req.command)
                    if req.command == 0x8005:
                        print 'list of devices'
                        conn.sendall(self.handle_device_list().pack())
                    elif req.command == 0x8003:
                        print 'attach device'
                        conn.recv(32)  # receive bus id
                        conn.sendall(self.handle_attach().pack())
                        attached = True
                else:
                    print 'handles requests'
                    cmd = USBIPCMDSubmit()
                    data = conn.recv(cmd.size())
                    cmd.unpack(data)
                    usb_req = USBRequest(seqnum=cmd.seqnum,
                                         devid=cmd.devid,
                                         direction=cmd.direction,
                                         ep=cmd.ep,
                                         flags=cmd.transfer_flags,
                                         numberOfPackets=cmd.number_of_packets,
                                         interval=cmd.interval,
                                         setup=cmd.setup,
                                         data=data)
                    self.usb_devices[0].connection = conn
                    self.usb_devices[0].handle_usb_request(usb_req)
            conn.close()

