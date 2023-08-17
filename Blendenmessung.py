"""

Name:       Blendenmessung 
Version:    0.3
Autor:      Sebastian Sturm
Datum:      22.04.2022
   
Massestromberechnung nach DIN EN ISO 5167-1 und DIN EN ISO 5167-2

"""

from numpy import sqrt, pi 
from CoolProp.CoolProp import PropsSI



class Blendenmessung(): 
    
    def __init__(self, D, d, p1, dp, T1, n = 8, ddp=20, dp1=90, dT1=1.0, dD=1.0E-5, dd=1.0E-5):
        
        self.D      = D                 # Rohrdurchmesser
        self.d      = d                 # Blendendurchmesser
        self.p1     = p1                # Druck vor der Blende
        self.dp     = dp                # Differenzdruck
        self.p2     = self.p1 - self.dp # Druck nach der Blende
        self.T1     = T1                # Temperatur vor der Blende
        self.n      = n                 # Genauigkeit der Massestromberechnung = 10^(-n)
        
        self.ddp = ddp                  # Fehler der Differenzdruckmessung
        self.dp1 = dp1                  # Fehler der Absolutdruckmessung
        self.dT1 = dT1                  # Fehler der Temperaturmessung
        self.dD  = dD                   # Fehler des Rohrdurchmessers
        self.dd  = dd                   # Fehler des Blendendurchmessers
        
        self.roh1   = PropsSI('D','P',self.p1,'T',self.T1,'air') # Dichte des Fluids vor der Blende
        self.mu1    = PropsSI('V','P',self.p1,'T',self.T1,'air') # Dyn. Viskosität des Fluids vor der Blende
        self.cp     = PropsSI('CPMASS','T',self.T1,'P',self.p1,'air') # isobaric heat capacity [J/Kg*K]
        self.cv     = PropsSI('CVMASS','T',self.T1,'P',self.p1,'air') # isochoric heat capacity [J/Kg*K]
        self.Rs     = 287.1
        
        self.beta   = d/D       # Durchmesserverhältnis
        
        
        self.kappa  = self.cp/self.cv   # Isentropenexponent
        # e = epsilon --> Expansionszahl
        self.e      = 1-(0.351+0.256*self.beta**4+0.93*self.beta**8)*(1-(self.p2/self.p1)**(1/self.kappa))         
        
        self.error_msg = ""
        
        # self.Run()
   
    
    def Massestrom(self):
             
        self.C = []         # Durchflusskoeffizient
        self.X = []         # Variable im linearen Algorithmus X1 = ReD = C * A1
        self.dx = []        # Differenz der Invariante und der Variable --> Konvergenzkriterium
        
        # Invariante A1
        self.A1 = self.e*self.d**2*sqrt(2*self.dp*self.roh1)/(self.mu1*self.D*sqrt(1-self.beta**4)) 
        
        self.C.append(0.606)                    # Startwert von C = 0.606 für Blenden
        self.X.append(self.C[0] * self.A1)      # X1 = ReD = C * A1
        self.dx.append(self.X[0] - self.A1)     # Eigentlich (X1 - A1) / A1
        
        self.i = 2
        
        # Linearer Algorithmus
        while abs(self.dx[-1]) > 10**(-self.n):
        # while abs((self.A1 - self.X[-1])/self.A1) > 10**(-self.n):
            
            self.A  = (19000*self.beta/(self.X[-1]))**0.8   # 
            
            if self.D > 71.12:
                
                self.C.append(
                    0.5961 + 0.0261*self.beta**2 - 0.216*self.beta**8 
                    + 0.000521*((10**6*self.beta)/(self.X[-1]))**0.7 
                    + (0.0188 + 0.0063 * self.A)*self.beta**3.5*(10**6/self.X[-1])**0.3) 
                + (0.043 + 0.08 - 0.123) * (1-0.11*self.A) * self.beta**4/(1-self.beta**4)
                    # Eckdruckentnahme --> 2. Zeile aus der Norm entfällt!!!
               
            else:
                self.C.append(
                    0.5961 + 0.0261*self.beta**2 - 0.216*self.beta**8 
                    + 0.000521*((10**6*self.beta)/(self.X[-1]))**0.7 
                    + (0.0188 + 0.0063 * self.A)*self.beta**3.5*(10**6/self.X[-1])**0.3) 
                + (0.043 + 0.08 - 0.123) * (1-0.11*self.A) * self.beta**4/(1-self.beta**4) 
                + (0.011*(0.75-self.beta)*(2.8-self.D/25.4)) 
                # Eckdruckentnahme --> 2. Zeile aus der Norm entfällt!!!
            """
            if self.i == 2:
                self.X.append(self.C[-1]*self.A1)
            else:
                self.X.append(self.X[-1]-self.dx[-1]*((self.X[-1] - self.X[-2])/(self.dx[-1] - self.dx[-2])))
            """
            
            self.X.append(self.C[-1]*self.A1)
            self.dx.append(self.X[-1] - self.X[-2])
            self.X.append(self.X[-1]-self.dx[-1]*((self.X[-1] - self.X[-2])/(self.dx[-1] - self.dx[-2])))
            
            # print([self.C[self.i-1], self.X[self.i-1], self.dx[self.i-1]])
            
            self.i = self.i + 1
        
        # Berechnung des Massestromes nach EN ISO 5167-1: 3.3.2.1 
        self.qm = pi/4 * self.mu1 * self.D * self.X[-1] 
        
        self.ReD = self.X[-1]                            # ReD = X1 = C * A1
    
    
    def Zulaessigkeit_pre(self):    # Prüfen der Durchmesserverhältnisse und Reynoldszahlen
        
        self.error_msg = []
    
        if self.d < 12.5E-3:
            self.error_msg.append( "Die Zulässigkeitsgrenze (d < 12.5) \nfür den Blendendurchmesser wurde unterschritten!" )
            
        if self.D < 50E-3:
            self.error_msg.append( "Die Zulässigkeitsgrenze (D < 50) \nfür den Rohrdurchmesser wurde unterschritten!" )
    
        if self.D > 1000E-3:
            self.error_msg.append( "Die Zulässigkeitsgrenze (D > 1000) \nfür den Rohrdurchmesser wurde überschritten!" )
            
        if self.beta < 0.1:
            self.error_msg.append( "Die Zulässigkeitsgrenze (beta < 0.1) \nfür das Durchmesserverhältnis wurde unterschritten!" )
            
        if self.beta > 0.75:
            self.error_msg.append( "Die Zulässigkeitsgrenze (beta > 0.75) \nfür das Durchmesserverhältnis wurde überschritten!" )
    
    
    def Zulaessigkeit_post(self):
    
        if self.beta >= 0.1 and self.beta <= 0.56 and self.ReD < 5000:
            self.error_msg.append("Die Zulässigkeitsgrenze (0.1 <= beta <= 0.56: ReD < 5000) \nfür die Rohr-Reynoldszahl wurde unterschritten! \nRe_D = " + str("{0:.0f}".format(self.ReD)) + ", beta= " + str("{0:.3f}".format(self.beta)))
            
        if self.beta > 0.56 and self.ReD < 16000*self.beta**2:
            self.error_msg.append("Die Zulässigkeitsgrenze (beta > 0.56: ReD < 1.6E+04*beta^2) \nfür die Rohr-Reynoldszahl wurde unterschritten! \nRe_D = " + str("{0:.0f}".format(self.ReD)) + ", beta= " + str("{0:.3f}".format(self.beta)))
    
    
    def Fehlerrechnung(self):
        
        self.droh1 = sqrt((self.dT1**2*self.p1**2)/(self.Rs**2*self.T1**4)+self.dp1**2/(self.Rs**2*self.T1**2))
        
        self.dC = 0
        
        if self.beta >= 0.1 and self.beta < 0.2:
            self.dC = (0.7 - self.beta)/100*self.C[-1]
        
        if self.beta >= 0.2 and self.beta < 0.6:
            self.dC = (0.5)/100*self.C[-1]
        
        if self.beta >= 0.6 and self.beta <= 0.75:
            self.dC = (1.667*self.beta-0.5)/100*self.C[-1]
            
        if self.D < 71.12E-3:
            self.dC0 = (0.9*(0.75-self.beta)*(2.8-(self.D/25.4)))/100*self.C[-1]
            self.dC = (self.dC + self.dC0)/2 # sqrt(self.dC**2 + self.dC0**2)
        
        if self.beta > 0.5 and self.X[-1] < 10000:
            self.dC1 = 0.5/100*self.C
            self.dC = (self.dC + self.dC1)/2 # sqrt(self.dC**2 + self.dC1**2)
        
        self.de = self.e * 3.5*self.dp/self.kappa/self.p1/100
        
        # Nach DIN EN ISO 5167-1: 8.2.2.1
        self.dqm = self.qm * sqrt((self.dC/self.C[-1])**2           # Fehler des Durchflusskoeffizienten
                    + (self.de/self.e)**2 + 1/4*(self.ddp/self.dp)**2  # Fehler der Expansionszahl
                    + 1/4*(self.droh1/self.roh1)**2                    # Fehler der Dichte (T, p)
                    + (2*self.beta**4/(1-self.beta**4))**2 * (self.dD/self.D)**2 # Fehler des Rohrdurchmessers
                    + (2/(1-self.beta**4))**2 * (self.dd/self.d)**2    # Fehler des Blendendurchmessers
                    )
        
        self.dqmp = self.dqm/self.qm*100
    
    
    def Ausgabe(self, mitfehlerrechnen=True):
        
        self.ausgabeliste = []
        
        self.ausgabeliste.append("Blendemessung: Massestrom")
        self.ausgabeliste.append("--------------------------------------------------------")
        self.ausgabeliste.append("Bezeichnung"+"\t\t\t"+"Größe"+"\t\t"+" Einheit")
        self.ausgabeliste.append("--------------------------------------------------------")
        self.ausgabeliste.append("Durchmesser D: \t\t\t"     +str("{0:.4f}".format(self.D))      +"\t\t m")
        self.ausgabeliste.append("Durchmesser d: \t\t\t"     +str("{0:.4f}".format(self.d))      +"\t\t m")
        self.ausgabeliste.append("D.-Verhältnis beta: \t\t"    +str("{0:.4f}".format(self.beta))   +"\t\t -")
        self.ausgabeliste.append(" ")
        self.ausgabeliste.append("Fluidtemperatur T1: \t\t"    +str("{0:.0f}".format(self.T1-273.15)) +"\t\t °C")
        self.ausgabeliste.append("Druck vor der Blende p1: \t" +str("{0:.0f}".format(self.p1))     +"\t\t Pa")
        self.ausgabeliste.append("Wirkdruck dp: \t\t\t"   +str("{0:.0f}".format(self.dp))     +"\t\t Pa")
        self.ausgabeliste.append(" ")
        
        if self.error_msg == []:
            
            self.ausgabeliste.append("Reynoldszahl Re_D: \t\t"       +str("{0:.0f}".format(self.ReD)) +"\t\t -")
            self.ausgabeliste.append("Durchflusskoeffizient C: \t"     +str("{0:.5f}".format(self.C[-1]))  +"\t\t -")
                        
            if mitfehlerrechnen:
                self.ausgabeliste.append(" ")
                self.ausgabeliste.append("Massestrom: \t\t\t"        +str("{0:.5f}".format(self.qm))     +"\t\t kg/s")
                self.ausgabeliste.append("Messfehler: \t\t\t"        +str("{0:.5f}".format(self.dqm))    +"\t\t kg/s")
                self.ausgabeliste.append("Messfehler: \t\t\t"        +str("{0:.5f}".format(self.dqmp))   +"\t\t %")
            
        else:
            for i in self.error_msg:
                self.ausgabeliste.append(i)
        
        self.ausgabeliste.append("--------------------------------------------------------")
        
        self.ausgabetext=""
        for i in self.ausgabeliste:
            self.ausgabetext = self.ausgabetext + i + "\n"
        
        return(self.ausgabetext)
        
    
    def Run(self):
        
        self.Zulaessigkeit_pre()
        self.Massestrom()
        self.Zulaessigkeit_post()
        self.Fehlerrechnung()
        print(self.Ausgabe())
        


if __name__ == "__main__":
    
    p1 = 110000
    dp =   8000
    T1 =    313
    
    blende = Blendenmessung(0.053, 0.0125, p1, dp, T1, 0.01e-3, 0.01e-3, 100, 12, 0.3)
    blende.Run()