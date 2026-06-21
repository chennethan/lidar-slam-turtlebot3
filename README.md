# Autonomous LiDAR SLAM Navigation — TurtleBot3

An autonomous mobile robot project built on ROS 2, combining LiDAR-based SLAM mapping with Nav2 path planning to achieve fully autonomous point-to-point navigation in a simulated environment.

## Overview

This project demonstrates an end-to-end autonomous navigation pipeline: a TurtleBot3 waffle robot maps an unknown environment using `slam_toolbox`, the resulting map is used by the Nav2 stack for global and local path planning, and the robot autonomously navigates to goal poses while avoiding obstacles — all validated in Gazebo simulation.

## Demo

![RViz2 path planning](docs/images/rviz_path_planning.png)
*Autonomous path planning visualized in RViz2 — global plan (full path) and local plan (immediate trajectory) shown over the costmap.*

<!-- Once you have a clip: ![Demo](docs/images/demo.gif) -->

## System Architecture

| Component | Tool |
|---|---|
| OS / Middleware | Ubuntu 24.04, ROS 2 Jazzy |
| Simulator | Gazebo Harmonic |
| Robot Model | TurtleBot3 Waffle |
| Mapping | `slam_toolbox` |
| Localization | AMCL |
| Path Planning | Nav2 (global + local planner) |
| Visualization | RViz2 |

**Pipeline:** `Gazebo (simulated LiDAR + odometry)` → `slam_toolbox (mapping)` → `map_saver_cli (saved map)` → `Nav2 + AMCL (localization & planning)` → `autonomous navigation`

> **Note:** This project targets ROS 2 Jazzy + Gazebo Harmonic, which differs in tooling from older ROS 2 Humble + Gazebo Classic tutorials (e.g. `gz` CLI instead of `gzserver`/`gzclient`). Some adaptation from community docs was required.

## Key Engineering Challenge: The AMCL/Nav2 Circular Dependency

One of the more interesting issues encountered during development was a deadlock between AMCL and Nav2 on startup.

**The problem:** After launching Nav2 with a saved map, the robot would never begin navigating — Nav2 appeared to hang indefinitely waiting for transforms.

**Root cause:** AMCL will not publish the `map → odom` transform until it receives an initial pose estimate. But Nav2's lifecycle manager times out waiting for the `map` frame to become available *before* an initial pose can be set through the normal RViz2 "2D Pose Estimate" tool — a circular dependency where each component is waiting on the other.

**The fix:** Publish a one-time initial pose directly to the `/initialpose` topic immediately after launching Nav2, bypassing the need to interact with RViz2 first:

```bash
ros2 topic pub --once /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: 'map'}, pose: {pose: {position: {x: 0.0, y: 0.0, z: 0.0}}}}"
```

This is now wrapped into a launch script ([`launch/init_pose.sh`](launch/init_pose.sh)) so the workaround is reproducible rather than manual.

**Why it matters:** This kind of timing/dependency issue is common in distributed robotics systems where multiple nodes have implicit startup-order assumptions. Diagnosing it required tracing the transform tree (`tf2`) and understanding the AMCL/Nav2 lifecycle rather than treating either as a black box.

## Map Details

![Saved map](docs/images/map_hexagonal_world.png)

- **Environment:** TurtleBot3 hexagonal world (Gazebo)
- **Resolution:** 0.05 m/pixel
- **Dimensions:** 112 × 103 px
- **Format:** `.pgm` (occupancy grid) + `.yaml` (metadata)
- **Generated via:** `slam_toolbox` SLAM + `map_saver_cli`

## How to Run

### Prerequisites
- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- TurtleBot3 packages (`turtlebot3`, `turtlebot3_simulations`, `nav2_bringup`, `slam_toolbox`)

### Launch sequence

This project uses three terminals in sequence:

```bash
# Terminal 1 — start the simulation
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py

# Terminal 2 — launch Nav2 with the saved map
ros2 launch nav2_bringup bringup_launch.py map:=maps/my_map.yaml

# Terminal 3 — seed the initial pose (resolves AMCL/Nav2 deadlock)
./launch/init_pose.sh
```

Nav2 opens its own RViz2 instance automatically — no separate RViz2 launch is needed. Once the map and robot pose appear aligned, use the **"Nav2 Goal"** tool in RViz2 to set a destination and watch the robot plan and execute the route autonomously.

### Re-mapping from scratch (optional)
```bash
ros2 launch turtlebot3_gazebo turtlebot3_world.launch.py
ros2 launch slam_toolbox online_async_launch.py
ros2 run teleop_twist_keyboard teleop_twist_keyboard   # drive around to build the map
ros2 run nav2_map_server map_saver_cli -f maps/my_map
```

## Results

✅ Full SLAM mapping of the test environment
✅ Resolved AMCL/Nav2 initialization deadlock
✅ Autonomous point-to-point navigation with live path planning in RViz2

## Roadmap

- [ ] Sequential multi-waypoint navigation (`nav2_simple_commander`)
- [ ] Obstacle avoidance validation against the saved map
- [ ] Costmap inflation radius tuning
- [ ] Frontier exploration (stretch goal)
- [ ] Demo video of full autonomous run
- [ ] Secondary project: robot arm with inverse kinematics + computer vision (ROS 2)

## Repository Structure

```
.
├── launch/        # Launch scripts (init_pose.sh, etc.)
├── maps/          # Saved occupancy grid maps (.pgm/.yaml)
├── config/        # Nav2 / AMCL parameter files
├── docs/
│   └── images/    # Screenshots and diagrams
└── README.md
```
