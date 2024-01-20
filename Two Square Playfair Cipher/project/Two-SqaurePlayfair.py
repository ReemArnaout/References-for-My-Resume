# -*- coding: utf-8 -*-
"""
Created on Sat Oct 21 16:41:48 2023

@author: Aya Al Baba & Reem Arnaout
"""
from flask import Flask,request, render_template
app = Flask(__name__)

def generate_matrix(keyword):
    keyword=keyword.upper()
    for i in range(len(keyword)):
        if keyword[i]=='J':
            keyword=keyword[:i]+'I'+keyword[i+1:]
    M=[[0 for i in range(5)] for j in range(5)]
    D={}
    k=0
    for i in range(5):
        for j in range(5):
            while k<len(keyword) and keyword[k] in D:
                k+=1
            if k>=len(keyword): break
            M[i][j]=keyword[k]
            D[keyword[k]]=1
            k+=1
        if k>=len(keyword): break
    letters='ABCDEFGHIKLMNOPQRSTUVWXYZ'
    k=0

    for i in range(5):
        for j in range(5):
            if M[i][j]!=0:
                continue
            while k<len(letters) and letters[k] in D:
                k+=1
            if k>=len(letters): break
            M[i][j]=letters[k]
            D[letters[k]]=1
            k+=1
        if k>=len(letters): break
    return M

##############################################################################################


def search_target(matrix,target):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == target:
                return i, j  
    return None


@app.route("/", methods=['POST','GET']) 
def main():
    plainstr=''
    cipherstr=''
    #Generating the Playfair 5x5 two-square matrices
    letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lettersall='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    keyword1=request.form.get('key1')   
    keyword2=request.form.get('key2')
    if keyword1 is not None and keyword1!='' and keyword2 is not None and keyword2!='':
        for i in range(len(keyword1)):
            if keyword1[i] not in lettersall:
                print("INVALID:The keyword has to be made of letters only!")   
                exit() 
        matrix1=generate_matrix(keyword1)
        for row in matrix1:
            for element in row:
                print(element, end=' ') 
            print()  
        print("This is Matrix 1")
        
        for i in range(len(keyword2)):
            if keyword2[i] not in lettersall:
                print("INVALID:The keyword has to be made of letters only!")   
                exit()
        matrix2=generate_matrix(keyword2)
        for row in matrix2:
            for element in row:
                print(element, end=' ') 
            print()  
        print ("This is Matrix 2")
        #Encryption Process
        plain=request.form.get('encrypt')
        if plain is not None and plain!='':
            plain=plain.upper()

            k=0
            for i in range(len(plain)):
                if plain[i]=='J':
                    plain=plain[:i]+'I'+plain[i+1:]
                if plain[i] not in letters:
                    k+=1

            cipher=[]
            i=0
            while i<len(plain):
                    if (i==(len(plain)-1)):
                        if (((len(plain)-k)%2)!=0) and (plain[i] in letters):
                            plain=plain+'X'
                        if (plain[i] not in letters):
                            cipher.append(plain[i]) 
                            break
                    x=search_target(matrix1,plain[i])
                    y=search_target(matrix2,plain[i+1])
                    if x==None and y!=None:
                        cipher.append(plain[i])
                        i+=1
                        continue
                    if x==None and y==None:
                        cipher.append(plain[i])
                        cipher.append(plain[i+1])
                        i+=2
                        continue
                    if x!=None and y==None:
                        plain=plain[:i+1]+'X'+plain[i+1:]
                        continue
                    if x[1]==y[1]:
                        cipher.append(matrix1[x[0]][x[1]])
                        cipher.append(matrix2[y[0]][y[1]])
                    if x[1]!=y[1]:
                        cipher.append(matrix1[x[0]][y[1]])
                        cipher.append(matrix2[y[0]][x[1]])
                    i+=2

            cipherstr=''.join(map(str,cipher))
            print("The encrypted text is: ", cipherstr)
        cipher=request.form.get('decrypt')
        if cipher is not None and cipher!='':
            #Decryption Process (same method as Encryption)
            cipher=cipher.upper()
            k=0
            for i in range(len(cipher)):
                if cipher[i]=='J':
                        cipher=cipher[:i]+'I'+cipher[i+1:]
                if cipher[i] not in letters:
                        k+=1
            plain=[]
            i=0
            while i<len(cipher):
                    if (i==(len(cipher)-1)):
                        if (((len(cipher)-k)%2)!=0) and (cipher[i] in letters):
                            cipher=cipher+'X'
                        if (cipher[i] not in letters):
                            plain.append(cipher[i]) 
                            break
                    x=search_target(matrix1,cipher[i])
                    y=search_target(matrix2,cipher[i+1])
                    if x==None and y!=None:
                        plain.append(cipher[i])
                        i+=1
                        continue
                    if x==None and y==None:
                        plain.append(cipher[i])
                        plain.append(cipher[i+1])
                        i+=2
                        continue
                    if x!=None and y==None:
                        cipher=cipher[:i+1]+'X'+cipher[i+1:]
                        continue
                    if x[1]==y[1]:
                        plain.append(matrix1[x[0]][x[1]])
                        plain.append(matrix2[y[0]][y[1]])
                    if x[1]!=y[1]:
                        plain.append(matrix1[x[0]][y[1]])
                        plain.append(matrix2[y[0]][x[1]])
                    i+=2
            plainstr=''.join(map(str,plain))
            print("The decrypted text is: ", plainstr)
    return render_template("index.html",encstr=cipherstr,decstr=plainstr)


if __name__ == "__main__":
    app.run()
