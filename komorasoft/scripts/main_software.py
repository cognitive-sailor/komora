from sensors_read import *

def main():
    print("Starting the main program.\n")
    # #sensors_read()
    # [T1,RH1,T2,RH2] = temp_humi_read()
    # [CO2,T3,RH3] = co2_temp_humi_read()
    # print(T1,T2,T3,RH1,RH2,RH3,CO2)
    while True:
        H2, O2, O2con = h2o2_read()
        print(H2," ",O2," ",O2con)

if __name__ == "__main__":
    main()
