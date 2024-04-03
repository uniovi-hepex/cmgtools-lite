from .producer import producer
from cfgs.samplepaths import samplepaths as paths
import os
class postprocessor_producer(producer):
  name = "postprocesor_producer"
  basecommand = "nanopy_batch.py"
  wz_cfg = "run_WZpostproc_fromNanoAOD_cfg.py"

  def add_more_options(self, parser):
    self.parser = parser
    parser.add_option("--outname", dest = "outname", type="string", default = paths["processed"]["mc"],
                      help = "Output (folder) name")
    parser.add_option("--analysis", dest = "analysis", type="string", default = "main",
                      help = "Output (folder) name")
    return
  
  def submit_InCluster(self):
    return self.command 

  def run(self):
    self.doData = "DATA" if self.isData else "MC"
    outname   = "/".join([self.outname])
    if self.isData: outname =  outname.replace("mc", "data")
   
      
    year     = self.year
    extra    = self.extra
    doData   = self.doData
  
  
    outname = os.path.join(outname, year)

    if self.analysis == "fr":
      outname = outname.replace(self.doData.lower(), self.doData.lower()+"_fr")
      self.extra += " --option analysis=%s"%self.analysis
    
    elif self.analysis == "fiducial":
      outname = outname.replace(self.doData.lower(), self.doData.lower()+"_unskim")
      self.extra += " --option analysis=%s"%self.analysis
      
    if self.local_test:
      outname = "prueba"
      self.extra += " --option justSummary=True"
    

    self.commandConfs = ["%s"%self.wz_cfg,
                    "-b 'sbatch batchScript.sh'",
                    "--option year='%s'"%year,
                    "--option selectComponents='%s'"%doData,
                    "--output-dir %s"%outname,
                    "%s"%self.extra]
    return
  
