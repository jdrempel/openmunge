def quat_to_rotation_matrix(quat):
    q0, q1, q2, q3 = map(float, quat)

    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)

    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)

    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1

    return [[r00, r01, r02],
            [r10, r11, r12],
            [r20, r21, r22]]


def mangle_quat(quat):
    q0, q1, q2, q3 = quat
    return [-q2, -q3, q0, -q1]
