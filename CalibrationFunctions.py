
def applyCalibrationFunction(calData, data, calibratedData):

    if calData[3] == "POL16":
        coeff = calData[2]              # Liste der vorhandenen Koeffizienten
        val = int(data, 16) / 65535     # Rohdaten Wert
        res = 0                         # Resultat auf 0 setzen
        for i in range(0, len(coeff)):
            res += coeff[i] * val ** i
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(res)
    
    elif calData[3] == "POL12":
        coeff = calData[2]              # Liste der vorhandenen Koeffizienten
        val = int(data, 16) / 4095      # Rohdaten Wert
        res = 0                         # Resultat auf 0 setzen
        for i in range(0, len(coeff)):
            res += coeff[i] * val ** i
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(res)
    
    elif calData[3] == "POL8":
        coeff = calData[2]              # Liste der vorhandenen Koeffizienten
        val = int(data, 16) / 255       # Rohdaten Wert
        res = 0                         # Resultat auf 0 setzen
        for i in range(0, len(coeff)):
            res += coeff[i] * val ** i
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(res)
    
    else:
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(int(data, 16))
