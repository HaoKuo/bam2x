#!/usr/bin/python
# programmer : zhuxp
# usage:
import sys
from getopt import getopt
import networkx as nx
import matplotlib.pyplot as plt

def show_help():
    print >>sys.stderr,"plotCausalGraph.py -m matrix"
    exit(0)
def Main():
    if len(sys.argv)==1: show_help()

    opts,restlist = getopt(sys.argv[1:],"m:oht:",\
                        ["matrix=","threshold=","help"])
    threshold=0.5
    for o, a in opts:
        if o in ("-m","matrix"): M = a
        if o in ("-h","--help"): show_help()
        if o in ("-t","--threshold"): threshold=float(a)
    try:
        f=open(M)
    except:
        print >>sys.stderr,"Can't open file",M
        show_help()
    max=0
    nodes=[]
    edges=[]
    pos={}
    edges_col=[]
    col={}
    
    rank={}
    lines=f.readlines()
    i=0
    for line in lines:
        line=line.strip()
        if line[0]=="#":continue
        a=line.split("\t")
        nodes.append(a[0])
        rank[a[0]]=0
        for k,x in enumerate(a[1:]):
            if k==i: continue
            x=float(x)
            if x>threshold or x<-threshold:
                if k < len(nodes) and rank[a[0]] < rank[nodes[k]]+1:
                    rank[a[0]]=rank[nodes[k]]+1
        if col.has_key(rank[a[0]]):
            col[rank[a[0]]]+=1
        else:
            col[rank[a[0]]]=1
        pos[a[0]]=(rank[a[0]],col[rank[a[0]]])
        i+=1


    j=0
 
    G=nx.DiGraph()
    G.add_nodes_from(nodes)
    for line in lines:
        line=line.strip()
        if line[0]=="#":continue
        a=line.split("\t")
        for i,x in enumerate(a[1:]):
            if i==j:continue
            x=float(x)
            if max<abs(x):max=abs(x)
            if x>threshold:
                G.add_edge(nodes[i],nodes[j],weight=x)
                edges_col.append(x)
            elif x<-threshold:
                G.add_edge(nodes[i],nodes[j],weight=x)
                edges_col.append(x)
        j+=1

    nx.draw(G,edge_cmap=plt.get_cmap("RdYlGn"),edge_color=edges_col,pos=pos,node_color="y",edge_vmin=-max,edge_vmax=max,linewidths=0)
    plt.colorbar()
    plt.show()




    
if __name__=="__main__":
    Main()

