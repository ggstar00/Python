import carla
import numpy as np
import cv2
import time
import random

actor_list = []
def process_img(image):
    i = np.array(image.raw_data)
    i2 = i.reshape((IM_HEIGHT,IM_WIDTH,4))
    i3 = i2[:,:,:3]
    print(i3)
    cv2.imshow("",i3)
    cv2.waitKey(1)
    return i3/255.0

try:
    # Connect to the server and start the client.
    client = carla.Client("localhost", 2000)
    client.set_timeout(2.0)

    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    bp = blueprint_library.filter("model3")[0]
    spawn_point = random.choice(world.get_map().get_spawn_points())
    vehicle = world.spawn_actor(bp, spawn_point)
    vehicle.apply_control(carla.VehicleControl(throttle=1.0,steer=0.0))
    actor_list.append(vehicle)
    
    IM_WIDTH = 640
    IM_HEIGHT = 480

    blueprint = blueprint_library.find('sensor.camera.rgb')
    blueprint.set_attribute("image_size_x", f"{IM_WIDTH}")
    blueprint.set_attribute("image_size_y", f"{IM_HEIGHT}")
    blueprint.set_attribute("fov", "110")

    
    spawn_point = carla.Transform(carla.Location(x=2.5,y=2, z=0.7))
    sensor = world.spawn_actor(blueprint, spawn_point, attach_to=vehicle)
    actor_list.append(sensor)

    sensor.listen(lambda data: process_img(data))
    time.sleep(5)

finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')


Show_preview = False

class CarEnv:
    def __init__(self,Show_preview,IM_WIDTH,IM_HEIGHT,front_camera=None,STEER_AMT=1.0,fov = 110):
        self.client = carla.Client('localhost',2000)
        self.client.set_timeout(2.0)
        self.world = self.client.get_world()

        blueprint_library = self.world.get_blueprint_library()

        self.model3 = blueprint_library.filter('model3')[0]
        self.Show_CAM = Show_preview
        self.im_width = IM_WIDTH
        self.im_height = IM_HEIGHT
        self.front_camera = front_camera
        self.fov = fov
        self.actor_list = []
        self.collision_hist = []

    def reset(self):
        self.collision_hist = []
        self.actor_list = []

        self.transform = random.choice(self.world.get_map().get_spawn_points())
        self.vehicle = self.world.spawn_actor(self.model3,self.transform)
        self.actor_list.append(self.vehicle)

        self.rgb_cam = self.world.get_blueprint_library().find('sensor.camera.rgb')
        self.rgb_cam.set_attribute("image_size_x",f'{self.im_width}')
        self.rgb_cam.set_attribute("image_size_y",f'{self.im_height}')
        self.rgb_cam.set_attribute("fov",f'{self.fov}')
    
        transform = carla.Transform(carla.Location(x = 2.5,z = 0.7))
        self.sensor = self.world.spawn_actor(self.rgb_cam,transform,attach_to=self.vehicle) #蓝图，位置，吸附到机器上
        self.actor_list.append(self.sensor)
        self.sensor.listen(lambda data: self.process_img(data))
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0,brake=0.0))

        time.sleep(4)
        colsensor = self.world.get_blueprint_library().find('sensor.other.collision')
        self.colsensor = self.world.spawn_actor(colsensor,transform,attach_to=self.vehicle)
        self.actor_list.append(self.colsensor)
        self.colsensor.listen(lambda data: self.collision_data(data))

        with self.front_camera is None:
            time.sleep(0.01)
        
        self.episode_start = time.time()
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0,brake=0.0))
        return self.front_camera





