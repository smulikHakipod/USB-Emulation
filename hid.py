import random
import datetime
from USBIP import BaseStucture, USBDevice, InterfaceDescriptor, DeviceConfigurations, EndPoint, USBContainer

# Emulating USB mouse

# HID Configuration

class HIDClass(BaseStucture):
    _fields_ = [
        ('bLength', 'B', 9),
        ('bDescriptorType', 'B', 0x21),  # HID
        ('bcdHID', 'H'),
        ('bCountryCode', 'B'),
        ('bNumDescriptors', 'B'),
        ('bDescriptprType2', 'B'),
        ('wDescriptionLength', 'H'),
    ]


hid_class = HIDClass(bcdHID=0x0100,  # Mouse
                     bCountryCode=0x0,
                     bNumDescriptors=0x1,
                     bDescriptprType2=0x22,  # Report
                     wDescriptionLength=0x3400)  # Little endian


interface_d = InterfaceDescriptor(bAlternateSetting=0,
                                  bNumEndpoints=1,
                                  bInterfaceClass=3,  # class HID
                                  bInterfaceSubClass=1,
                                  bInterfaceProtocol=2,
                                  iInterface=0)

end_point = EndPoint(bEndpointAddress=0x81,
                     bmAttributes=0x3,
                     wMaxPacketSize=8000,  # Little endian
                     bInterval=0xFF)  # interval to report


configuration = DeviceConfigurations(wTotalLength=0x2200,
                                     bNumInterfaces=0x1,
                                     bConfigurationValue=0x1,
                                     iConfiguration=0x0,  # No string
                                     bmAttributes=0x80,  # valid self powered
                                     bMaxPower=50)  # 100 mah current

interface_d.descriptions = [hid_class]  # Supports only one description
interface_d.endpoints = [end_point]  # Supports only one endpoint
configuration.interfaces = [interface_d]   # Supports only one interface


class USBHID(USBDevice):
    vendorID = 0x0627
    productID = 0x0
    bcdDevice = 0x0
    bcdUSB = 0x0
    bNumConfigurations = 0x1
    bNumInterfaces = 0x1
    bConfigurationValue = 0x1
    configurations = []
    bDeviceClass = 0x0
    bDeviceSubClass = 0x0
    bDeviceProtocol = 0x0
    configurations = [configuration]  # Supports only one configuration

    def __init__(self):
        USBDevice.__init__(self)
        self.start_time = datetime.datetime.now()

    def generate_mouse_report(self):

        arr = [0x05, 0x01,		# Usage Page (Generic Desktop)
               0x09, 0x02,		# Usage (Mouse)
               0xa1, 0x01,		# Collection (Application)
               0x09, 0x01,		#   Usage (Pointer)
               0xa1, 0x00,		#   Collection (Physical)
               0x05, 0x09,		#     Usage Page (Button)
               0x19, 0x01,		#     Usage Minimum (1)
               0x29, 0x03,		#     Usage Maximum (3)
               0x15, 0x00,		#     Logical Minimum (0)
               0x25, 0x01,		#     Logical Maximum (1)
               0x95, 0x03,		#     Report Count (3)
               0x75, 0x01,		#     Report Size (1)
               0x81, 0x02,		#     Input (Data, Variable, Absolute)
               0x95, 0x01,		#     Report Count (1)
               0x75, 0x05,		#     Report Size (5)
               0x81, 0x01,		#     Input (Constant)
               0x05, 0x01,		#     Usage Page (Generic Desktop)
               0x09, 0x30,		#     Usage (X)
               0x09, 0x31,		#     Usage (Y)
               0x09, 0x38,		#     Usage (Wheel)
               0x15, 0x81,		#     Logical Minimum (-0x7f)
               0x25, 0x7f,		#     Logical Maximum (0x7f)
               0x75, 0x08,		#     Report Size (8)
               0x95, 0x03,		#     Report Count (3)
               0x81, 0x06,		#     Input (Data, Variable, Relative)
               0xc0,		#   End Collection
               0xc0]		# End Collection
        return_val = ''
        for val in arr:
            return_val+=chr(val)
        return return_val

    def handle_data(self, usb_req):
        # Sending random mouse data
        # Send data only for 5 seconds
        if (datetime.datetime.now() - self.start_time).seconds < 5:
            return_val = chr(0x0) + chr(random.randint(1, 10)) + chr(random.randint(1, 10)) + chr(random.randint(1, 10))
            self.send_usb_req(usb_req, return_val)


    def handle_unknown_control(self, control_req, usb_req):
        if control_req.bmRequestType == 0x81:
            if control_req.bRequest == 0x6:  # Get Descriptor
                if control_req.wValue == 0x22:  # send initial report
                    print 'send initial report'
                    self.send_usb_req(usb_req, self.generate_mouse_report())

        if control_req.bmRequestType == 0x21:  # Host Request
            if control_req.bRequest == 0x0a:  # set idle
                print 'Idle'
                # Idle
                pass


usb_Dev = USBHID()
usb_container = USBContainer()
usb_container.add_usb_device(usb_Dev)  # Supports only one device!
usb_container.run()

# Run in cmd: usbip.exe -a 127.0.0.1 "1-1"