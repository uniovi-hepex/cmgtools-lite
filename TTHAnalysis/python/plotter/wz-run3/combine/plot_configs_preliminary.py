""" configuration file for making postfit plots """
import ROOT as r


class plot( object ):
    """ Description of a plot """
    def __init__(self, name):
        self.name = name

        # >> Things for the x axis
        self.rangex = None
        self.binlabels = []

        # >> Things for the y axis
        self.force_y_max = None
        self.ScaleUpperY = 1.1  
        self.ymin_ratio = 0.7
        self.ymax_ratio = 1.3
        self.logy = False

        # >> Title 
        self.titleX = "My variable"
        self.titleY = "Events"
        
        # >> Legend
        self.leg_x0 = 0.22
        self.leg_x1 = 0.42
        self.leg_y0 = 0.82
        self.leg_ncolumns = 1
        self.leg_height = 7 # This is a factor applied to the following formula: leg_ymin = 0.9 - leg_textsize * 1.15 * leg_height


        # >> Keep here your spams
        self.spams = {
            "lumi" : {
                "text" : "__LUMI__ fb^{-1} (13.6 TeV)", 
                "x0"   : .65, 
                "y0"   : .963, 
                "x1"   : .975, 
                "y1"   : .99, 
                "textsize" : 22
            },
            "cmsprel" : {
                # With preliminary --- for PAS
                "text" : "#splitline{#scale[1.2]{#bf{CMS}}}{#scale[1.0]{#it{Preliminary}}}",
                "x0"   : .2, 
                "y0"   : .825, 
                "x1"   : .35, 
                "y1"   : .865, 
                "textsize" : 22
                #"text" : "#splitline{#scale[1.2]{#bf{CMS}}}{}",
                #"x0"   : .2, 
                #"y0"   : .870, 
                #"x1"   : .35, 
                #"y1"   : .885, 
                #"textsize" : 22        
            },

            "fit" : {
                "text" : '#splitline{#scale[1.2]{__REGIONLABEL__}}{#scale[1.0]{__FITLABEL__}}', 
                "x0"   : .75, 
                "y0"   : .825, 
                "x1"   : .90, 
                "y1"   : .865, 
                "textsize" : 22
            }
        }
        return

    def modify_spam(self, label, field, value):
        self.spams[label][field] = value
        return self

    def get_legend(self, entries):
        """ Fixed format for a one column legend """
        leg_textsize = 0.05616
        leg_height = len(entries) // self.leg_ncolumns
        width = 0.2*(1 + 1.05*self.leg_ncolumns)
        height = leg_textsize * ( 1.30 - 0.03*self.leg_ncolumns ) * leg_height
        legend = r.TLegend(self.leg_x0, self.leg_y0, self.leg_x0 + width, self.leg_y0 + height) 
        legend.SetBorderSize(0)
        legend.SetFillColor(0)
        legend.SetShadowColor(0)
        legend.SetFillStyle(0)
        legend.SetTextFont(42)
        legend.SetTextSize( leg_textsize )
        legend.SetNColumns( self.leg_ncolumns )
        return legend


# -- Define the 3l flavor plot 
class flavor3l_plot(plot):
    def __init__(self):
        plot.__init__(self, "flavor3l")
        self.titleX = "Lepton flavor"
        self.binlabels = ["eee", "ee#mu", "#mu#mue", "#mu#mu#mu"]
        
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.21
            self.leg_y0 = 0.52
            self.ScaleUpperY = 1.25
            
            #self.ymin_ratio = 0.8
            #self.ymax_ratio = 1.2
            #self.modify_spam("fit", "x0", 0.2)
            #self.modify_spam("fit", "x1", 0.35)
            #self.modify_spam("fit", "y0", 0.705)
            #self.modify_spam("fit", "y1", 0.745)
        if region == "crzz":
            self.leg_ncolumns = 1    
            self.leg_x0 = 0.38
            self.leg_y0 = 0.55
            self.ScaleUpperY = 1.2
            
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.38
            self.leg_y0 = 0.69
            self.ScaleUpperY = 1.4
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crconv":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.21
            self.leg_y0 = 0.35
            self.ScaleUpperY = 1.1
            self.modify_spam("fit", "x0", 0.79)
            self.modify_spam("fit", "x1", 0.85)
            #self.modify_spam("fit", "y0", 0.860)
            #self.modify_spam("fit", "y1", 0.875)
            
class lepZ1_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepZ1_pt")
        self.titleX = r"#it{p}_{T} (l_{Z}^{1}) (GeV)"
        self.titleY = r"Events / 10 GeV"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38
            self.ScaleUpperY = 1.25
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)
        if region == "crzz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32
            self.ScaleUpperY = 1.25
        if region == "crtt":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38  
            self.ScaleUpperY = 1.65
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)

        if region == "crconv":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32  
            self.ScaleUpperY = 1.3

class lepZ2_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepZ2_pt")
        self.titleX = r"#it{p}_{T} (l_{Z}^{2}) (GeV)"
        self.titleY = r"Events / 10 GeV"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38
            self.ScaleUpperY = 1.20
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)
        if region == "crzz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32
            self.ScaleUpperY = 1.3
        if region == "crtt":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38  
            self.ScaleUpperY = 1.4
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)

        if region == "crconv":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32  
            self.ScaleUpperY = 1.3

class lepW_pt_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepW_pt")
        self.titleX = r"#it{p}_{T} (l_{W}) (GeV)"
        self.titleY = r"Events / 10 GeV"

              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38
            self.ScaleUpperY = 1.17
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)
        if region == "crzz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32
            self.ScaleUpperY = 1.45
        if region == "crtt":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38  
            self.ScaleUpperY = 1.3
            self.modify_spam("fit", "x0", 0.4)
            self.modify_spam("fit", "y0", 0.835)
            self.modify_spam("fit", "y1", 0.875)

        if region == "crconv":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.54
            self.leg_y0 = 0.32  
            self.ScaleUpperY = 1.25

class lepZ1_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepZ1_eta")
        self.titleX = r"#eta l_{Z}^{1}"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.66
            self.ScaleUpperY = 1.6
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crzz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.40
            self.leg_y0 = 0.67
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.69
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crconv":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.65
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

class lepZ2_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepZ2_eta")
        self.titleX = r"#eta l_{Z}^{2}"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.66
            self.ScaleUpperY = 1.6
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crzz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.40
            self.leg_y0 = 0.67
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.67
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crconv":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.65
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)


class lepW_eta_plot(plot):
    def __init__(self):
        plot.__init__(self, "lepW_eta")
        self.titleX = r"#eta l^{W}"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.66
            self.ScaleUpperY = 1.6
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crzz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.40
            self.leg_y0 = 0.64
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.67
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

        if region == "crconv":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.65
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

class nJets(plot):
    def __init__(self):
        plot.__init__(self, "nJets")
        self.titleX = r"Number of jets"
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.59
            self.leg_y0 = 0.22
            self.ScaleUpperY = 1.4
        if region == "crzz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.59
            self.leg_y0 = 0.22
            self.ScaleUpperY = 1.4
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.44
            self.leg_y0 = 0.64
            self.ScaleUpperY = 1.8
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crconv":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.59
            self.leg_y0 = 0.22
            self.ScaleUpperY = 1.6

class m3l(plot):
    def __init__(self):
        plot.__init__(self, "m3l")
        self.titleX = r"#it{m}(l_{Z}^{1}, l_{Z}^{2}, l_{W}) (GeV)"
        self.titleY = r"Events / 20 GeV"

              
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1    
        self.leg_x0 = 0.62
        self.leg_y0 = 0.41
        self.ScaleUpperY = 1.2
        self.modify_spam("fit", "x0", 0.44)
        self.modify_spam("fit", "x1", 0.59)
        self.modify_spam("fit", "y0", 0.805)
        self.modify_spam("fit", "y1", 0.845)
        if region == "srwz":
            self.leg_ncolumns = 1
            self.leg_x0 = 0.62
            self.leg_y0 = 0.41
            self.ScaleUpperY = 1.3
            self.modify_spam("fit", "x0", 0.44)
            self.modify_spam("fit", "x1", 0.59)
            self.modify_spam("fit", "y0", 0.805)
            self.modify_spam("fit", "y1", 0.845)
        if region == "crzz":
            self.leg_ncolumns = 1
            self.leg_x0 = 0.57
            self.leg_y0 = 0.45
            self.ScaleUpperY = 1.2
            self.modify_spam("fit", "x0", 0.44)
            self.modify_spam("fit", "x1", 0.59)
            self.modify_spam("fit", "y0", 0.805)
            self.modify_spam("fit", "y1", 0.845)
        if region == "crtt":
            self.leg_ncolumns = 1
            self.leg_x0 = 0.57
            self.leg_y0 = 0.42
            self.ScaleUpperY = 1.2
            self.modify_spam("fit", "x0", 0.44)
            self.modify_spam("fit", "x1", 0.59)
            self.modify_spam("fit", "y0", 0.805)
            self.modify_spam("fit", "y1", 0.845)


class mll_3l(plot):
    def __init__(self):
        plot.__init__(self, "mll_3l")
        self.titleX = r"#it{m}(l_{Z}^{1}, l_{Z}^{2}) (GeV)"
        self.titleY = r"Events / 2 GeV"

              
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1     
        self.leg_x0 = 0.61
        self.leg_y0 = 0.38
        self.ScaleUpperY = 1.1
        self.modify_spam("fit", "x0", 0.2)
        self.modify_spam("fit", "x1", 0.35)
        self.modify_spam("fit", "y0", 0.705)
        self.modify_spam("fit", "y1", 0.745)

class met(plot):
    def __init__(self):
        plot.__init__(self, "met")
        self.titleX = r"#it{p}_{T}^{miss} (GeV)"
        self.titleY = r"Events / 7 GeV"
              
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1     
        self.leg_x0 = 0.61
        self.leg_y0 = 0.38
        self.ScaleUpperY = 1.1
        self.modify_spam("fit", "x0", 0.44)
        self.modify_spam("fit", "x1", 0.59)
        self.modify_spam("fit", "y0", 0.805)
        self.modify_spam("fit", "y1", 0.845)
        if region == "crtt":
            self.leg_ncolumns = 2
            self.leg_x0 = 0.39
            self.leg_y0 = 0.69
            self.ScaleUpperY = 1.45
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

class mll_3l_mm(mll_3l):
    def __init__(self):
        mll_3l.__init__(self)
        self.titleX = r"#it{m}(#mu_{Z}^{1}, #mu_{Z}^{2}) (GeV)"
        self.rangex = (80, 100)
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1     
        self.ScaleUpperY = 1.1
        if region == "srwz":
            self.titleY = r"Events / 1.0 GeV"
            self.leg_x0 = 0.20
            self.leg_y0 = 0.30
            self.force_y_max = 370
        if region == "crzz":
            self.titleY = r"Events / 0.5 GeV"
            self.force_y_max = 65
            self.leg_x0 = 0.61
            self.leg_y0 = 0.38
            
            self.rangex = (85, 100)    
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)        
        else:
            pass


class mll_3l_ee(mll_3l):
    def __init__(self):
        mll_3l.__init__(self)
        self.titleX = r"#it{m}(e_{Z}^{1}, e_{Z}^{2}) (GeV)"
        self.rangex = (80, 105)
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1     
        self.ScaleUpperY = 1.1
        if region == "srwz":
            self.leg_ncolumns = 1     
            self.leg_x0 = 0.63
            self.leg_y0 = 0.34
            self.ScaleUpperY = 1.4
            self.titleY = r"Events / 1.0 GeV"
            self.force_y_max = 160 
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745) 
        if region == "crzz":
            self.force_y_max = 25
            self.leg_x0 = 0.22
            self.leg_y0 = 0.38    
            self.rangex = (85, 95)
            self.titleY = r"Events / 0.4 GeV"
            #self.modify_spam("fit", "x0", 0.2)
            #self.modify_spam("fit", "x1", 0.35)
            #self.modify_spam("fit", "y0", 0.705)
            #self.modify_spam("fit", "y1", 0.745)        
        else:
            pass


class met(plot):
    def __init__(self):
        plot.__init__(self, "met")
        self.titleX = r"#it{p}_{T}^{miss} (GeV)"
        self.titleY = r"Events / 7 GeV"
              
    def modify(self, region):
        """ Apply custom styling """
        self.leg_ncolumns = 1     
        self.leg_x0 = 0.61
        self.leg_y0 = 0.38
        self.ScaleUpperY = 1.1
        self.modify_spam("fit", "x0", 0.44)
        self.modify_spam("fit", "x1", 0.59)
        self.modify_spam("fit", "y0", 0.805)
        self.modify_spam("fit", "y1", 0.845)

class charge(plot):
    def __init__(self):
        plot.__init__(self, "charge")
        self.binlabels = [r"l_{W} (-)", r"l_{W} (+)"]
        self.titleX = "Final state charge"
        self.rangex = [-1.5,1.5]
              
    def modify(self, region):
        """ Apply custom styling """
        if region == "srwz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.39
            self.leg_y0 = 0.69
            self.ScaleUpperY = 1.35
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if  region == "crzz":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.39
            self.leg_y0 = 0.73
            self.ScaleUpperY = 1.49
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if region == "crtt":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.39
            self.leg_y0 = 0.70
            self.ScaleUpperY = 1.41
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)
        if  region == "crconv":
            self.leg_ncolumns = 2     
            self.leg_x0 = 0.39
            self.leg_y0 = 0.70
            self.ScaleUpperY = 1.49
            self.modify_spam("fit", "x0", 0.2)
            self.modify_spam("fit", "x1", 0.35)
            self.modify_spam("fit", "y0", 0.705)
            self.modify_spam("fit", "y1", 0.745)

plots = {
    "flavor3l"  : flavor3l_plot(),
    "lepZ1_pt"  : lepZ1_pt_plot(),
    "lepZ2_pt"  : lepZ2_pt_plot(),
    "lepW_pt"   : lepW_pt_plot(),
    "lepZ1_eta" : lepZ1_eta_plot(),
    "lepZ2_eta" : lepZ2_eta_plot(),
    "lepW_eta"  : lepW_eta_plot(),
    "nJets"     : nJets(),
    "m3l"       : m3l(),
    "mll_3l"    : mll_3l(),
    "mll_3l_ee"    : mll_3l_ee(),
    "mll_3l_mm"    : mll_3l_mm(),
    "met"       : met(),
    "charge"    : charge()
}
