
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
            t1 = int(data[i], 16) / 65535
            t2 = int(data[diffChannels[0]], 16) / 65535
            t3 = int(data[diffChannels[1]], 16) / 65535
            coeff1 = calData[i][2]
            coeff3 = calData[diffChannels[1]][2]

            tempRes1 = 0
            tempRes2 = 0
            for k in range(0, len(coeff1)):
                tempRes1 += coeff1[k] * (t1-t2) ** (len(coeff1)-1-k)

            for k in range(0, len(coeff3)):
                tempRes2 += coeff3[k] * t3 ** (len(coeff3)-1-k)

            res = tempRes1 + tempRes2
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

        elif calData[i][3] == "NTC":
            pass    # TODO: Weitere fehlende KalFunkTypen hinzufügen

        else:
            calibratedData["UUID"].append(calData[i][0])
            calibratedData["DATA"].append(int(data[i], 16))

    return calibratedData
