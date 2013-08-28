#!/usr/bin/env python
# Programmer : zhuxp
# Date: 
# Last-modified: 08-28-2013, 16:07:08 EDT
VERSION="0.3"
'''
xQuery.py is an example program for using xplib.DBI interface
it reports the overlap features or data from the query region.

the query file format can be:
bed,vcf,genebed etc.

the database or data file can be:
bam,tabix,vcf,bed,genebed etc.

for tabix ant other genome annotation file ,
    it yield the overlap annotations in this region
for bam file
    it yield the Nucleotides Distribution in each site of this region.
Example:
    xQuery.py -i file.bed -a file.bam
'''
import os,sys,argparse
from xplib.Annotation import *
from xplib import Tools,TableIO
import pysam
from xplib import DBI
import signal
signal.signal(signal.SIGPIPE,signal.SIG_DFL)
import time
import numpy
import xplib
def ParseArg():
    ''' This Function Parse the Argument '''
    p=argparse.ArgumentParser( description = 'Example: %(prog)s -i file.snp -a file.vcf.gz -A tabix -o output.file', epilog='Library dependency : pysam xplib')
    p.add_argument('-v','--version',action='version',version='%(prog)s '+VERSION)
    p.add_argument('-i','--input',dest="input",type=str,default="stdin",help="input file")
    p.add_argument('-I','--format',dest="input_format",type=str,help="input file format",default="bed")
    p.add_argument('-A','--dbformat',dest="dbformat",type=str,help="input file database format. {bed|genebed|tabix|bam}",default="bam")
    p.add_argument('-o','--output',dest="output",type=str,default="stdout",help="output file")
    p.add_argument('-a','--annotations',dest="db",type=str,default="",required=True,help="query annotation files")
    p.add_argument('-m','--query_method',dest="query_method",type=str,help="query method : ( bamfile: pileup or fetch or fetch12 (splicing reads) ; bigwig: cDNA or not ; twobit: seq | cDNA | cds | utr3 | utr5 )")
    p.add_argument('-s','--silence',dest="silence",action='store_true',help="only report hits number")
    if len(sys.argv)==1:
        print >>sys.stderr,p.print_help()
        exit(0)
    return p.parse_args()


def Main():
    global args,out
    args=ParseArg()
    dict={}
    if args.output=="stdout":
        out=sys.stdout
    else:
        try:
            out=open(args.output,"w")
        except IOError:
            print >>sys.stderr,"can't open file ",args.output,"to write. Using stdout instead"
            out=sys.stdout
    argv=sys.argv
    argv[0]=argv[0].split("/")[-1]
    print >>out,"# This data was generated by program ",argv[0],"(version %s)"%VERSION,
    print >>out,"in bam2x ( https://github.com/nimezhu/bam2x )"
    print >>out,"# Date: ",time.asctime()
    print >>out,"# The command line is :\n#\t"," ".join(argv)
    if args.query_method:
        dict["method"]=args.query_method
    dbi=DBI.init(args.db,args.dbformat)
    hits=0
    query=0
    if args.input=="stdin":
        input=sys.stdin
    else:
        input=args.input

    query_length=0
    hits_number=0
    for (i0,x) in enumerate(TableIO.parse(input,args.input_format)):
        if i0%10==0:
            print >>sys.stderr,"query ",i0," entries\r",
        print >>out,"QR\t",x
        hit=0
        query+=1
        query_length+=len(x)
        results=dbi.query(x,**dict)
        compatible=0
        #print >>sys.stderr,type(results)
        if isinstance(results,numpy.ndarray) or isinstance(results,list):
            if not args.silence:
                print >>out,"HT\t",
                for value in results:
                    print >>out,str(value)+",",
                print >>out,""
            hit=1
            hits_number+=1
        elif isinstance(results,str):
            if not args.silence:
                print >>out,"HT\t",
                print >>out,results
            hit=1
            hits_number+=1

        else:
            for j in results:
                if not args.silence:
                    print >>out,"HT\t",j,
                hit=1
                hits_number+=1
                if isinstance(j,xplib.Annotation.Bed12) and isinstance(x,xplib.Annotation.Bed12):
                    compatible_binary=Tools.compatible_with_transcript(j,x)
                    if not args.silence:
                        print >>out,"\tCompatible:",compatible_binary
                    if compatible_binary:
                        compatible+=1
                else:
                    if not args.silence:
                        print >>out,""
            print >>out,"TT\t",hits_number
            if compatible>0:
                print >>out,"CP\t",compatible

        if args.dbformat=="tabix":
            x.chr=x.chr.replace("chr","")
            for j in dbi.query(x,**dict):
                print >>out,"HT\t",j
                hit=1
                hits_number+=1
        hits+=hit
    print >>out,"# Query Number:",query,"\n# Query Have Hits:",hits
    print >>out,"# Query Length:",query_length
    print >>out,"# Hits Number:",hits_number
    
if __name__=="__main__":
    Main()




