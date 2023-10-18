
def isValidDiffChannels(diffChannels: list, data, numberOfChannels: int = 0):
    if type(diffChannels) != list:
        print("Type of column DifferenzKanal is not a list!")
        return False
    if len(diffChannels) != numberOfChannels:
        print("Length of list DifferenzKanal is not 2!")
        return False
    for i in range(0, numberOfChannels):
        if diffChannels[i] >= len(data):
            print("DifferenzKanal[0] is out of index of data list! | diffChannel: ", diffChannels[i])
            return False
    return True


def applyCalibrationFunctions(calData, data):
    calibratedData = {"UUID": [], "DATA": []}

    for i in range(0, len(data) - 1):
        if calData[i][3] == "POL16":
            coeff = calData[i][2]               # Liste der vorhandenen Koeffizienten
            val = int(data[i], 16) / 65535      # Rohdaten Wert
            res = 0                             # Resultat auf 0 setzen
            for k in range(0, len(coeff)):
                res += coeff[k] * val ** (len(coeff)-1-k)
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)

        elif calData[i][3] == "POL12":
            coeff = calData[i][2]               # Liste der vorhandenen Koeffizienten
            val = int(data[i], 16) / 4095       # Rohdaten Wert
            res = 0                             # Resultat auf 0 setzen
            for k in range(0, len(coeff)):
                res += coeff[k] * val ** (len(coeff)-1-k)
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)

        elif calData[i][3] == "POL10":
            coeff = calData[i][2]               # Liste der vorhandenen Koeffizienten
            val = int(data[i], 16) / 1023       # Rohdaten Wert
            res = 0                             # Resultat auf 0 setzen
            for k in range(0, len(coeff)):
                res += coeff[k] * val ** (len(coeff)-1-k)
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)
        
        elif calData[i][3] == "POL8":
            coeff = calData[i][2]               # Liste der vorhandenen Koeffizienten
            val = int(data[i], 16) / 255        # Rohdaten Wert
            res = 0                             # Resultat auf 0 setzen
            for k in range(0, len(coeff)):
                res += coeff[k] * val ** (len(coeff)-1-k)
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)





        elif calData[i][3] == "POL16TED2":
            diffChannels = calData[i][4]        # Liste der Differenzkanäle ("D2" ~ 2 Differenzkanälen [Thermoelement, Thermistor])
            if not isValidDiffChannels(diffChannels, data, 2):
                continue
            t1 = int(data[i], 16) / 65535                   # dig des TE Messwertes
            t2 = int(data[diffChannels[0]], 16) / 65535     # dig der TE Ref-Stelle
            t3 = int(data[diffChannels[1]], 16) / 65535     # dig des Ref-Thermistors
            coeff1 = calData[i][2][0]                       # Koeffizienten der Thermopaarung
            coeff2 = calData[i][2][1]                       # Koeffizienten der Spannungskalibrierung
            coeff3 = calData[diffChannels[1]][2]            # Koeffizienten der Thermistorkalibrierung

            tempRes1 = 0    # Differenztemperatur der Messstelle zur Referenzstelle
            tempRes2 = 0    # Temperatur der Referenzstelle
            vRes     = 0    # Thermospannung
            
            # Umrechnen der Digitdifferenz in eine TE-Spannung
            for k in range(0, len(coeff2)):
                vRes += coeff2[k] * (t1-t2) ** (len(coeff2)-1-k)
            
            # Umrechnen der TE-Spannung in eine Temperatur
            for k in range(0, len(coeff1)):
                tempRes1 += coeff1[k] * vRes ** (len(coeff1)-1-k)
                # tempRes1 += coeff1[k] * (t1-t2) ** (len(coeff1)-1-k)

            # Umrechnen der Ref-Th Digit in eine Temperatur
            for k in range(0, len(coeff3)):
                tempRes2 += coeff3[k] * t3 ** (len(coeff3)-1-k)

            res = tempRes1 + tempRes2
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)




        elif calData[i][3] == "POL16DruckPlusBaro":
            diffChannels = calData[i][4]
            if not isValidDiffChannels(diffChannels, data, 1):
                continue

            t1 = int(data[i], 16) / 65535
            t2 = int(data[diffChannels[0]], 16) / 65535

            coeff1 = calData[i][2]
            coeff2 = calData[diffChannels[0]][2]

            DDRes = 0
            DARes = 0
            for k in range(0, len(coeff1)):
                DDRes += coeff1[k] * t1 ** (len(coeff1)-1-k)

            for k in range(0, len(coeff2)):
                DARes += coeff2[k] * t2 ** (len(coeff2)-1-k)

            res = DARes + DDRes
            # res = res/1e5 # Ausgabe  in bar

            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)
            

        elif calData[i][3] == "RPM2HEX":
            diffChannels = calData[i][4]        # Liste des Differenzkaal
            if not isValidDiffChannels(diffChannels, data, 1):
                continue
            val1 = int(data[i], 16)
            val2 = int(data[diffChannels[0]], 16)
            coeff1 = calData[i][2][0]

            res = coeff1*60/(val1 * 65536 + val2)

            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)

        # elif calData[i][3] == "TIME":
        #     diffChannels = calData[i][4]
        #     if not isValidDiffChannels(diffChannels, data, 1):
        #         continue
        #     tcnt0 = int(data[i], 16)
        #     tcnt1 = int(data[diffChannels[0]], 16)
        #     fT = calData[i][2][0]
            
        #     res = (tcnt0 * 65536 + tcnt1) / fT
            
        #     t_diff = [0]
        #     for j in range(1, len(res)):
        #         if (res[j] - res[j-1]) > 0 :
        #             t_diff.append(res[j] - res[j-1] + t_diff[j-1])
        #         else:
        #             t_diff.append(res[j] + 2**32/fT - res[j-1] + t_diff[-1])
        #     t_diff = np.array(t_diff)
            
        #     calibratedData["UUID"].append(calData[i][0])
        #     calibratedData["DATA"].append(t_diff)
            
        elif calData[i][3] == "UKONTR":
            diffChannels = calData[i][4]
            if not isValidDiffChannels(diffChannels, data, 1):
                continue
            padx  = int(data[i], 16)
            pad0  = int(data[diffChannels[0]], 16)
            koeff = calData[i][2][0]
            
            res = koeff * padx/pad0
            
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)
            
        elif calData[i][3] == "UREF":
            padx  = int(data[i], 16)
            koeff = calData[i][2][0]
            
            res = koeff * 1023/padx
            
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(res)
            
        # elif calData[i][3] == "TPROZ":
        #     padx  = int(data[i], 16)
        #     T25 = calData[i][2][0]
        #     Ra  = calData[i][2][1]
        #     R25 = calData[i][2][2]
        #     B   = calData[i][2][3]
            
        #     res = (1/T25 + np.log(Ra*(1023/padx-1)/R25)/B)**(-1) - 273.15
            
        #     calibratedData["UUID"].append(calData[i][0])
        #     calibratedData["DATA"].append(res)
            
        # elif calData[i][3] == "TPROZ_OV":
        #     padx  = int(data[i], 16)
        #     T25 = calData[i][2][0]
        #     R25 = calData[i][2][1]
        #     B   = calData[i][2][2]
            
        #     Rth = 68000 / (31.3 * padx/1023 - 1) - 2200
        #     res = (1/T25 + np.log(Rth/R25)/B)**(-1) - 273.15
            
        #     calibratedData["UUID"].append(calData[i][0])
        #     calibratedData["DATA"].append(res)
        
        elif calData[i][3] == "NTC":
            pass    # TODO: Weitere fehlende KalFunkTypen hinzufügen

        else:
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(int(data[i], 16))

    return calibratedData
