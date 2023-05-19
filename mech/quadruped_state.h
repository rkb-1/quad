// Copyright 2014-2020 Josh Pieper, jjp@pobox.com.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#pragma once

#include <optional>

#include "sophus/se3.hpp"

#include "mjlib/base/visitor.h"

#include "base/kinematic_relation.h"
#include "base/point3d.h"
#include "base/quaternion.h"

#include "mech/quadruped_command.h"

namespace mjmech {
namespace mech {

struct QuadrupedState {
  // The joint level.
  struct Joint {
    int id = 0;

    // These are the raw values reported by the actuator and are not
    // referenced to any particular frame.
    double angle_deg = 0.0;
    double velocity_dps = 0.0;
    double torque_Nm = 0.0;

    double temperature_C = 0.0;
    double voltage = 0.0;
    int32_t mode = 0;
    int32_t fault = 0;

    double kp_Nm = 0.0;
    double ki_Nm = 0.0;
    double kd_Nm = 0.0;
    double feedforward_Nm = 0.0;
    double command_Nm = 0.0;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(id));
      a->Visit(MJ_NVP(angle_deg));
      a->Visit(MJ_NVP(velocity_dps));
      a->Visit(MJ_NVP(torque_Nm));
      a->Visit(MJ_NVP(temperature_C));
      a->Visit(MJ_NVP(voltage));
      a->Visit(MJ_NVP(mode));
      a->Visit(MJ_NVP(fault));
      a->Visit(MJ_NVP(kp_Nm));
      a->Visit(MJ_NVP(ki_Nm));
      a->Visit(MJ_NVP(kd_Nm));
      a->Visit(MJ_NVP(feedforward_Nm));
      a->Visit(MJ_NVP(command_Nm));
    }
  };

  std::vector<Joint> joints;

  // The leg end-effector level.
  struct Leg {
    enum Mode {
        kStanceAllLeg,
        kSwingOneLeg,
        kDone,
      };
    Mode mode = kStanceAllLeg;
    int leg = 0;
    base::Point3D position;
    base::Point3D velocity;
    base::Point3D force_N;
    double stance = 0.0;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(mode));
      a->Visit(MJ_NVP(leg));
      a->Visit(MJ_NVP(position));
      a->Visit(MJ_NVP(velocity));
      a->Visit(MJ_NVP(force_N));
      a->Visit(MJ_NVP(stance));
    }

    friend Leg operator*(const Sophus::SE3d&, const Leg& rhs);
  };

  std::vector<Leg> legs_B;
  Leg leg_onemove, pee_behavior;


  struct Traj_replay {
    enum Mode {
        kInitPose,
        kExertion,
        kFlight,
        kLand,
        kDone,
      };
    Mode mode = kInitPose;
    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(mode));
    }
  };
  Traj_replay replay_behavior;

  
  // And finally, the robot level.
  struct Robot {
    // Only v[0, 1] and w[2] will be non-zero.
    base::KinematicRelation desired_R;

    // Mappings between the B (body) frame, and the R (robot), M
    // (CoM), and A (attitude) frames.
    base::KinematicRelation frame_RB;
    base::KinematicRelation frame_MB;
    base::KinematicRelation frame_AB;

    // Transform from the CoM frame to the terrain frame.
    std::array<double, 2> terrain_rad = {};
    Sophus::SE3d tf_TA;

    double voltage = 0.0;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(desired_R));

      a->Visit(MJ_NVP(frame_RB));
      a->Visit(MJ_NVP(frame_MB));
      a->Visit(MJ_NVP(frame_AB));

      a->Visit(MJ_NVP(terrain_rad));
      a->Visit(MJ_NVP(tf_TA));
      a->Visit(MJ_NVP(voltage));
    }
  };

  Robot robot;

  // Now the state associated with various control modes.  Each mode's
  // data is only valid while that mode is active.

  struct StandUp {
    enum Mode {
      kPrepositioning,
      kStanding,
      kDone,
    };

    Mode mode = kPrepositioning;
    int prepositioning_stage = 0;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(mode));
      a->Visit(MJ_NVP(prepositioning_stage));
    }
  };

  StandUp stand_up;

  struct Rest {
    bool done = false;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(done));
    }
  };

  Rest rest;

  struct Jump {
    enum Mode {
      kLowering = 0,
      kPushing = 1,
      kRetracting = 2,
      kFalling = 3,
      kLanding = 4,
      kDone = 5,
    };

    Mode mode = kLowering;
    double velocity = 0.0;
    double acceleration = 0.0;

    QuadrupedCommand::Jump command;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(mode));
      a->Visit(MJ_NVP(velocity));
      a->Visit(MJ_NVP(acceleration));
      a->Visit(MJ_NVP(command));
    }
  };

  Jump jump;

  struct Walk {
    int idle_count = 0;

    struct Leg {
      base::Point3D target_R;
      double invalid_time_s = 0.0;

      // From the idle R frame position, what balanced travel distance
      // can be achieved at the current command.
      double travel_distance = 0.0;

      // What velocity is needed to restore to a neutral standing
      // position.
      double restore_velocity = 0.0;
      double restore_remaining = 0.0;

      // Is this leg currently locked into contact with the ground?
      bool latched = false;

      template <typename Archive>
      void Serialize(Archive* a) {
        a->Visit(MJ_NVP(target_R));
        a->Visit(MJ_NVP(invalid_time_s));
        a->Visit(MJ_NVP(travel_distance));
        a->Visit(MJ_NVP(restore_velocity));
        a->Visit(MJ_NVP(restore_remaining));
        a->Visit(MJ_NVP(latched));
      }
    };

    std::array<Leg, 4> legs;

    struct VLeg {
      double remaining_s = 0.0;
      double invalid_time_s = 0.0;
      enum Mode {
        kStance,
        kSwing,
      };
      Mode mode = kStance;
      double swing_elapsed_s = 0.0;
      double stance_elapsed_s = 0.0;
      double phase_s = 0.0;
      double target_time_s = 0.0;
      Eigen::Vector3d predicted_next_v;

      template <typename Archive>
      void Serialize(Archive* a) {
        a->Visit(MJ_NVP(remaining_s));
        a->Visit(MJ_NVP(invalid_time_s));
        a->Visit(MJ_NVP(mode));
        a->Visit(MJ_NVP(swing_elapsed_s));
        a->Visit(MJ_NVP(stance_elapsed_s));
        a->Visit(MJ_NVP(phase_s));
        a->Visit(MJ_NVP(target_time_s));
        a->Visit(MJ_NVP(predicted_next_v));
      }
    };

    std::array<VLeg, 2> vlegs;
    int next_step_vleg = 0;
    double stance_elapsed_s = 0.0;
    base::Point3D last_swing_v_R;
    // The minimum travel distance of any leg.
    double travel_distance = 0.0;

    struct Trot {
      double swing_time = 0.0;
      double onevleg_time = 0.0;
      double twovleg_time = 0.0;
      double flight_time = 0.0;
      double speed = 0.0;
      double max_speed = 0.0;

      template <typename Archive>
      void Serialize(Archive* a) {
        a->Visit(MJ_NVP(swing_time));
        a->Visit(MJ_NVP(onevleg_time));
        a->Visit(MJ_NVP(twovleg_time));
        a->Visit(MJ_NVP(flight_time));
        a->Visit(MJ_NVP(speed));
        a->Visit(MJ_NVP(max_speed));
      }
    };

    Trot trot;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(idle_count));
      a->Visit(MJ_NVP(legs));
      a->Visit(MJ_NVP(vlegs));
      a->Visit(MJ_NVP(next_step_vleg));
      a->Visit(MJ_NVP(stance_elapsed_s));
      a->Visit(MJ_NVP(last_swing_v_R));
      a->Visit(MJ_NVP(travel_distance));
      a->Visit(MJ_NVP(trot));
    }
  };

  Walk walk;

  struct Backflip {
    enum Mode {
      kLowering = 0,
      kFrontPush = 1,
      kBackPush = 2,
      kFlight = 3,
      kDone = 4,
    };

    Mode mode = kLowering;
    double pitch_deg = 0.0;
    double pitch_rate_dps = 0.0;
    double pitch_accel_dps2 = 0.0;
    double velocity = 0.0;

    template <typename Archive>
    void Serialize(Archive* a) {
      a->Visit(MJ_NVP(mode));
      a->Visit(MJ_NVP(pitch_deg));
      a->Visit(MJ_NVP(pitch_rate_dps));
      a->Visit(MJ_NVP(pitch_accel_dps2));
      a->Visit(MJ_NVP(velocity));
    }
  };

  Backflip backflip;

  template <typename Archive>
  void Serialize(Archive* a) {
    a->Visit(MJ_NVP(joints));
    a->Visit(MJ_NVP(legs_B));
    a->Visit(MJ_NVP(leg_onemove));
    a->Visit(MJ_NVP(pee_behavior));
    a->Visit(MJ_NVP(replay_behavior));
    a->Visit(MJ_NVP(robot));

    a->Visit(MJ_NVP(stand_up));
    a->Visit(MJ_NVP(rest));
    a->Visit(MJ_NVP(jump));
    a->Visit(MJ_NVP(walk));
    a->Visit(MJ_NVP(backflip));
  }
};

inline QuadrupedState::Leg operator*(const Sophus::SE3d& pose_AB,
                                     const QuadrupedState::Leg& rhs_B) {
  auto result_A = rhs_B;
  result_A.position = pose_AB * rhs_B.position;
  result_A.velocity = pose_AB.so3() * rhs_B.velocity;
  result_A.force_N = pose_AB.so3() * rhs_B.force_N;
  return result_A;
}

}
}

namespace mjlib {
namespace base {

template <>
struct IsEnum<mjmech::mech::QuadrupedState::StandUp::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::StandUp::Mode;
  static inline std::map<M, const char*> map() {
    return {
      { M::kPrepositioning, "prepositioning" },
      { M::kStanding, "standing" },
      { M::kDone, "done" },
    };
  }
};

template <>
struct IsEnum<mjmech::mech::QuadrupedState::Jump::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::Jump::Mode;

  static inline std::map<M, const char*> map() {
    return {
      { M::kLowering, "lowering" },
      { M::kPushing, "pushing" },
      { M::kRetracting, "retracting" },
      { M::kFalling, "falling" },
      { M::kLanding, "landing" },
      { M::kDone, "done" },
    };
  }
};

template <>
struct IsEnum<mjmech::mech::QuadrupedState::Backflip::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::Backflip::Mode;

  static inline std::map<M, const char*> map() {
    return {
      { M::kLowering, "lowering" },
      { M::kFrontPush, "front_push" },
      { M::kBackPush, "back_push" },
      { M::kFlight, "flight" },
      { M::kDone, "done" },
    };
  }
};

template <>
struct IsEnum<mjmech::mech::QuadrupedState::Walk::VLeg::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::Walk::VLeg::Mode;

  static inline std::map<M, const char*> map() {
    return {
      { M::kStance, "stance" },
      { M::kSwing, "swing" },
    };
  }
};

template <>
struct IsEnum<mjmech::mech::QuadrupedState::Leg::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::Leg::Mode;

  static inline std::map<M, const char*> map() {
    return {
      { M::kStanceAllLeg, "stanceAllLeg" },
      { M::kSwingOneLeg, "swingOneLeg" },
      { M::kDone, "done" },
    };
  }
};
template <>
struct IsEnum<mjmech::mech::QuadrupedState::Traj_replay::Mode> {
  static constexpr bool value = true;

  using M = mjmech::mech::QuadrupedState::Traj_replay::Mode;

  static inline std::map<M, const char*> map() {
    return {
      { M::kInitPose, "initPose" },
      { M::kExertion, "exertion" },
      { M::kFlight, "flight" },
      { M::kLand, "landing" },
      { M::kDone, "done" },
    };
  }
};

}
}
