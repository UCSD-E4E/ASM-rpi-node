# Animal Flipper
The overall objective of this device is to provide an Aye-Aye simulator.

This device programmatically moves a stuffed lemur into and out of the box.

We have designated 3 key labels:
1. In Frame
2. Partial Frame
3. Out of Frame

This system does have some troubles with accurate locating of the animal when the motors are disengaged, so we shall make effort to always home the arm.

The home position is the most "in" frame that the animal can be.  We can find this location by rotating in the home direction for at least `motor_steps`.

We can then define a threshold value that determines the point at which the animal starts exiting the frame.  We define this to be `out_threshold_steps` from home.

We can then define another threshold that determines the point at which the animal is completely out of the frame.  We define this to be at `out_frame_steps` from home.

Note that during these, the arm is dragging the stuffed animal out of the box.  Thus, the behavior will be different when dragging the animal back into the box.

We define another location `safe_steps` that places the stuffed animal fully out of frame and enables it to switch directions seamlessly.  This is the point at which the stuffed animal direction will switch.

We define the `in_frame_steps` to be the point at which the animal starts to come back into the frame.

We define the `in_threshold_steps` to be the point at which the animal is fully back into the frame.

We also define a `loiter_time_s`, which is the time that the stuffed animal will loiter either at the home or safe positions.

To ensure reliable locating, we will not disable the motors during any phase of this.  When we loiter at home, we will always drive into the home stop by a quarter rotation to ensure that we are fully at the home location.

Labels are provided as the timestamp at the start of that label.  All data up to the next timestamp is that label.