import csv
import constants
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy import interpolate

LEFT_ANKLE_TO_MOTOR = np.array(
    [4.93809841e-06, -9.37236976e-04, -1.91799432e-02,  1.49927256e+00,
    5.50444115e+02,  1.48885144e+04])
RIGHT_ANKLE_TO_MOTOR = np.array(
    [-7.58737033e-06,  1.26704441e-03,  1.43450629e-02, -2.14108179e+00,
    -5.47623518e+02,  9.62346598e+03]
)

folder = 'calibration_files/'
for filename in ["20220228_2140__RIGHT.csv"]:
    # filename = "20220228_2138__LEFT.csv" #"20220225_1314__LEFT.csv"
    with open(folder + filename) as f:
        motor_angle = [int(row["motor_angle"])
                       for row in csv.DictReader(f)]
    with open(folder + filename) as f:
        ankle_angle = [np.floor(float(row["ankle_angle"]))
                       for row in csv.DictReader(f)]
    ankle_angle = np.array(ankle_angle)[5:] 
    motor_angle = np.array(motor_angle)[5:]*constants.ENC_CLICKS_TO_DEG

    plt.figure(1)
    plt.xlabel('ankle angle')
    plt.ylabel('motor angle')
    plt.plot(ankle_angle, motor_angle)
    # Sort the data points
    zipped_sorted_lists = sorted(zip(ankle_angle, motor_angle))
    mytuples = zip(*zipped_sorted_lists)
    ankle_angle, motor_angle = [
        list(mytuple) for mytuple in mytuples]
    plt.plot(ankle_angle, motor_angle)

    # Filter
    b, a = signal.butter(N=1, Wn=0.05)
    motor_angle = signal.filtfilt(
        b, a, motor_angle, method="gust")
    ankle_angle = signal.filtfilt(
        b, a, ankle_angle, method="gust")
    plt.plot(ankle_angle, motor_angle)

    # Calculate Gradient
    TR = np.gradient(motor_angle)/np.gradient(ankle_angle)

    # Polyfit
    p = np.polyfit(ankle_angle, motor_angle /
                   constants.ENC_CLICKS_TO_DEG, deg=5)
    print('Polynomial coefficients: ', p)
    polyfitted_left_motor_angle = np.polyval(p, ankle_angle)
    plt.plot(ankle_angle, polyfitted_left_motor_angle)

    pcurrent = RIGHT_ANKLE_TO_MOTOR
    polyfitted_left_motor_angle = np.polyval(pcurrent, ankle_angle)
    plt.plot(ankle_angle, polyfitted_left_motor_angle, linestyle='dashed')

    plt.figure(2)
    p_deriv = np.polyder(p)
    TR_from_polyfit = np.polyval(p_deriv, ankle_angle)
    plt.plot(ankle_angle, -TR_from_polyfit*constants.ENC_CLICKS_TO_DEG)

    p = np.polyfit(ankle_angle, TR, deg=4)
    deriv_left2 = np.polyval(p, ankle_angle)

    plt.plot(ankle_angle, -TR)

    ankle_pts = [-60, -30, -20, 0, 15, 30, 40, 45.6, 55, 80]
    deriv_pts = [-23, -11.5, -11, -12,-12.5, -12, -10, -8, -3, 9]

    # ANKLE_PTS = np.array([-60, -40, 0, 10, 20, 30, 40, 45.6, 55, 80])  # Deg
    # TR_PTS = np.array([16, 16, 15, 14.5, 14, 11.5, 5, 0, -6.5, -12])  # Nm/Nm
    
    deriv_spline_fit = interpolate.pchip_interpolate(
        ankle_pts, deriv_pts, ankle_angle)
    plt.plot(ankle_angle, -1* deriv_spline_fit, linewidth=5)

    # deriv_spline_fit_2 = interpolate.pchip_interpolate(
    #     ANKLE_PTS, TR_PTS, ankle_angle)
    # plt.plot(ankle_angle, deriv_spline_fit_2, linewidth=5)
    # plt.xlim([-50, 80])
    # plt.ylim([-22, 22])
    plt.ylabel('Transmission Ratio')
    plt.xlabel('Ankle Angle')

plt.show()
