#include <iostream>
using namespace std;
#include <vector>
#include <string>


class _15puzzle {
    vector<vector<int>> v; //this is the nxn two dimensional grid
    static int n;
    //v[i][j]=0 is the empty spot
    int i;
    int j;
    public:
    const _15puzzle * parent; //will be used to track solution
    _15puzzle(){
        i=n-1;
        j=n-1;
        for (int x=0;x<n;x++){
            v[x].resize(n);
        }
        parent=NULL;


        int k=1;
            for (int y=0; y<n;y++){
        for (int x=0;x<n;x++){
                v[x][y]=k;
                k++;
        }
        }
        v[n-1][n-1]=0;
    }

    _15puzzle(const vector<vector<int>> vv) {
        v=vv;bool correct=false;parent = NULL;
        for (int x=0;x<n;x++){
            for (int y=0;y<n;y++){
                if (v[x][y]==0){
                    i=x;
                    j=y;
                    correct=true;
                    break;
                }
            }
            if (correct){
                break;
            }
        }
    }

    vector<_15puzzle> neighbors(){
        vector<_15puzzle> k;
        _15puzzle k1(*this);_15puzzle k2(*this);_15puzzle k3(*this);_15puzzle k4(*this);
        if (i>0){
            k1.i=i-1;
            k1.v[i][j]=k1.v[i-1][j];
            k1.v[i-1][j]=0;
            k.push_back(k1);
        }
        if (i<n-1){
            k4.i=i+1;
            k4.v[i][j]=k4.v[i+1][j];
            k4.v[i+1][j]=0;
            k.push_back(k4);
        }
        if (j>0){
            k2.j=j-1;
            k2.v[i][j]=k2.v[i][j-1];
            k2.v[i][j-1]=0;
            k.push_back(k2);
        }
        if (j<n-1){
            k3.j=j+1;
            k3.v[i][j]=k3.v[i][j+1];
            k3.v[i][j+1]=0;
            k.push_back(k3);
        }
        return k;
    }

    //yes, no return type should be specified since it must return a string
    operator string()const {
    //make it return a string representation of the configuration
        string s;
        for (int x=0;x<n;x++){
            for (int y=0;y<n;y++){
                if (v[x][y]==0)
                    s=s+'A';
                else if (v[x][y]==1)
                    s=s+'B';
                else if (v[x][y]==2)
                    s=s+'C';
                else if (v[x][y]==3)
                    s=s+'D';
                else if (v[x][y]==4)
                    s=s+'E';
                else if (v[x][y]==5)
                    s=s+'F';
                else if (v[x][y]==6)
                    s=s+'G';
                else if (v[x][y]==7)
                    s=s+'H';
                else if (v[x][y]==8)
                    s=s+'I';
            }
        }
        return s;
    }
    bool operator==(const _15puzzle& p)const{
        return (this->operator std::string()==p.operator std::string());
    }
    friend ostream& operator<<(ostream&s,_15puzzle p);
};
int _15puzzle::n=3;
ostream& operator<<(ostream&s, _15puzzle p){
    for(int x=0;x<3;x++){
        for(int y=0;y<3;y++){
            if(p.v[x][y]==0){s<<" "<<" ";}
            else{s<<p.v[x][y]<< " ";}
        }
    }
    return s;
}




_15puzzle scramble(const _15puzzle& p, int moves) {
//start with q=p
    _15puzzle q;
    q=p;
//1. generate the neighbors vector of q
    vector<_15puzzle> c;
//2. choose a random neighbor r from the vector
    int r;
    
//3. make q=r
    
//4. repeat n times from 1

//return q
    return q;

}
//typedef your unordered_map as HT
int main() {
    srand(time(0));
    _15puzzle p;
    _15puzzle q=scramble(p, 50); //or p.scramble(50) if inside the class
    
}

