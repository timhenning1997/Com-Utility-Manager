
def applyCalibrationFunction(calData, data, calibratedData):
    # calData[0]    ~   UUID            Type: Str           Bsp.: GeraetXY_Messstelle_Z0
    # calData[1]    ~   Name            Type: Str           Bsp.: PAD0_0
    # calData[2]    ~   KalKoeff        Type: valid JSON    Bsp.: [12, 13, 14]
    # calData[3]    ~   KalFunkTyp      Type: Str           Bsp.: POL16
    # calData[4]    ~   DifferenzKanal  Type: Int           Bsp.: 3
    # calData[5]    ~   Messwert        Type: Str           Bsp.: TE
    # calData[6]    ~   FitFehler       Type: Float         Bsp.: 50.9
    # calData[7]    ~   Kommentar       Type: valid JSON    Bsp.: []

    # data          ~   Messwert als Hexstring              Bsp.: 0F32

    if calData[3] == "POL16":
        coeff = calData[2]              # Liste der vorhandenen Koeffizienten
        val = int(data, 16) / 65535     # Rohdaten Wert
        res = 0                         # Resultat auf 0 setzen
        for i in range(0, len(coeff)):
            res += coeff[i] * val ** i
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(res)
    else:
        calibratedData["UUID"].append(calData[0])
        calibratedData["DATA"].append(int(data, 16))
