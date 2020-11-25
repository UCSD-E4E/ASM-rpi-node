from onvif import ONVIFCamera
mycam = ONVIFCamera('192.168.2.64', 80, 'admin','NyalaChow22',wsdl_dir = '/home/pi/python-onvif/wsdl')

time_params = mycam.devicemgmt.create_type('SetSystemDateAndTime')
time_params.DateTimeType = 'Manual'
time_params.DaylightSavings = True
time_params.TimeZone.TZ= 'PST-8:00:00'
time_params.UTCDateTime.Date.Year = 2020
time_params.UTCDateTime.Date.Month = 10
time_params.UTCDateTime.Date.Day = 28
time_params.UTCDateTime.Time.Hour = 12
time_params.UTCDateTime.Time.Minute = 55
time_params.UTCDateTime.Time.Second = 50
mycam.devicemgmt.SetSystemDateAndTime(time_params)
