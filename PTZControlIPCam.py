from onvif import ONVIFCamera
from time import sleep

XMAX = 1
XMIN = -1
YMAX = 1
YMIN = -1

def perform_move(ptz, request, timeout):
    ptz.ContinuousMove(request)
    sleep(timeout)
    request.PanTilt=1
    ptz.Stop(request)

def move_up(ptz, request, timeout=2):
    print 'move up...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMAX
    perform_move(ptz, request, timeout)

def move_down(ptz, request, timeout=2):
    print 'move down...'
    request.Velocity.PanTilt._x = 0
    request.Velocity.PanTilt._y = YMIN
    perform_move(ptz, request, timeout)

def move_right(ptz, request, timeout=2):
    print 'move right...'
    request.Velocity.PanTilt._x = XMAX
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def move_left(ptz, request, timeout=2):
    print 'move left...'
    request.Velocity.PanTilt._x = XMIN
    request.Velocity.PanTilt._y = 0
    perform_move(ptz, request, timeout)

def continuous_move():
    mycam = ONVIFCamera('192.168.2.64',80, 'admin','NyalaChow22',wsdl_dir='/home/pi/python-onvif/wsdl');
    media = mycam.create_media_service();
    ptz = mycam.create_ptz_service();

    media_profile = media.GetProfiles()[0];
    #print media_profile

    request = ptz.create_type('GetConfigurationOptions');
    request.ConfigurationToken = media_profile.PTZConfiguration._token
    ptz_configuration_options = ptz.GetConfigurationOptions(request)

    request = ptz.create_type('ContinuousMove');
    request.ProfileToken = media_profile._token;

    global XMAX,XMIN,YMAX,YMIN
    XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
    XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
    YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
    YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min

    move_right(ptz, request)
    move_left(ptz,request)
    move_up(ptz,request)
    move_down(ptz,request)

if __name__ == '__main__':
    continuous_move()


