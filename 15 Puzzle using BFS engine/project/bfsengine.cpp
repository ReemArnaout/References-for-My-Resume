#include <bits/stdc++.h>
#include <iostream>
#include<unordered_map>
using namespace std;
#include<queue>
#include "_15puzzle.cpp"

class hashfct{
    public:
        size_t operator()(const _15puzzle& p) const{return hash<string>()(p.operator std::string());}
};

typedef unordered_map<_15puzzle,int,hashfct> HT;

int BFS(const _15puzzle& start, const _15puzzle& end,HT& ht, int iter_max=1000){

    vector<_15puzzle> k;queue<_15puzzle> q;_15puzzle p /*current one were on*/ ;int iter=0;bool correct=false;
    q.push(start);
    ht[start]=0;
    if (iter==iter_max){
            return -1;
    }
    while(!q.empty()&&iter<iter_max){
        iter++;
        p=q.front();
        q.pop();
        k=p.neighbors();
        
        for(int t=0;t<k.size();t++){
            if(k[t]==end){
                correct=true;
                end==k[t];
                break;
            }
            if(ht.find(k[t])==ht.end()){
                q.push(k[t]);
                k[t].parent=&(ht.find(p)->first); // address since const
                ht[k[t]]=ht[p]+1;
                
                
                if(p==start){k[t].parent=&start;}
            }
        }
    }
    return iter;
}


vector<_15puzzle> path(const _15puzzle p, HT& ht){
    vector<_15puzzle> k;_15puzzle x=p;
    while (x.parent!=NULL){
        k.push_back(x);
        x=*x.parent;
    }
    if (ht.find(p)==ht.end()){
        return k;
    }
    return k;
    k.push_back(x);
}


