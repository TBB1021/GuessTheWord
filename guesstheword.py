import random
import threading
import time
import re

class Main():
    def __init__(self):
        g=Game()
        repeat=True
        opt=input("Welcome to Guess The Word \n(1)New Game \n(2)Load Game \n(3)Highscore \n(4)Exit \nChoose a option:")
        while not re.search(r'^[1-4]{1}$',opt):
            opt=input("Invalid Input. Try Again:")
        if opt=="1" or opt=="2":
            name=str(input("Enter Game Name:"))
            if opt=="1":
                while g.check(name):
                    name=str(input("File Name Already Exist. Please Reenter:"))
                g.new(name)
            elif opt=="2":
                while not g.check(name):
                    name=str(input("Game Save Can Not Be Found. Please Reenter:"))
                g.load(name)
            while repeat:
                g.play()
                again=str(input("Would you like to play again (Y|N):")).upper()
                if again=="N":
                    repeat=False
                    g.save()
            Main()
        elif opt=="3":
            g.leaderboard()
            Main()
        elif opt=="4":
            print("Guess The Word Program Terminated")
            
class Game():
    def __init__(self):
        self.hs=0
        self.words=[]
        self.hard=False
        self.hints=False
        self.newgame=True
        self.rpn=RPNStack()
    
    def new(self,name):
        self.name=name
        words=open("100words.txt","r")
        self.words=[]
        if str(input("Enable Hard Mode(Y|N):")).upper() =="Y":
            self.hard=True
        if str(input("Enable Hints(Y|N):")).upper() =="Y":
            self.hints=True
            print("Just Enter 101 and a letter of the word will be revealed")
        for word in words:
            word=word.rstrip()
            self.words.append(word)
           
    def load(self,name):
        with open("games.txt","r") as f:
            for line in f:
                data=eval(line)
                if data["Game Name"]==name:
                    self.name=data["Game Name"]
                    self.words=data["Words To Guess"]
                    self.hard=data["Hard Mode"]
                    self.hints=["Hint Mode"]
                    self.hs=data["High Score"]
                    self.newgame=False
    
    def play(self):
        complete=False
        trys=[]
        lock=threading.Lock()
        word=list(self.words[random.randint(0,len(self.words)-1)])
        gtw=[]
        for letter in list(word):
            gtw.append("_")
        print("Score:",self.hs)
        print(' '.join(gtw))
        t=threading.Thread(target=self.penalty,args=(),daemon=True)
        t.start()      
        while complete==False:
            correct=False
            self.guess=None    
            self.guess=str(input("Type Your Guess:"))
            print(self.hs)
            while self.guess in trys:
                self.guess=str(input("You Have Already Entered That. Please Reenter Guess:"))
            trys.append(self.guess)
            lock.acquire()
            if self.guess=="101" and self.hints:
                hint=word[random.randint(0,len(word)-1)]
                for x in range(len(gtw)):
                    if hint==word[x]:
                        correct=True
                        gtw.insert(x,hint)
                        gtw.pop(x+1)
                        trys.append(hint)
                self.hs=self.rpn.Start(self.hs,1,"-")
                print("You have used up your hint for this round and lost 1 point")
                print(' '.join(gtw))
            elif len(list(self.guess))==1:
                for x in range(len(gtw)):
                    if self.guess==word[x]:
                        correct=True
                        gtw.insert(x,self.guess)
                        gtw.pop(x+1)
                if correct==False:
                    print("You have guessed the incorrect letter\n")
                    self.hs=self.rpn.Start(self.hs,2,"-")
                else:
                    print("You have guessed the right letter\n")
                    self.hs=self.rpn.Start(self.hs,2,"+")
                print(''.join(gtw))
            elif self.guess!=''.join(word):
                print("You are incorrect\n")
                self.hs=self.rpn.Start(self.hs,5,"-")
                print(''.join(gtw))
            if self.guess==''.join(word) or ''.join(word)==''.join(gtw):
                complete=True
                self.hs=self.rpn.Start(self.hs,10,"+")
                print("Completed")
                print("Your score so far is",self.hs)
            lock.release()
        print("[",''.join(word),"]")
        self.words.remove(''.join(word))
        print("You have guessed the correct word")
        t.join()
       
    def save(self):
        data={"Game Name": self.name, "High Score":self.hs, "Words To Guess":self.words, "Hard Mode":self.hard, "Hint Mode":self.hints}
        if self.newgame==False:
            dicts=[]
            with open("games.txt","r") as f:
                for line in f:
                    dicts.append(line)
            with open("games.txt","w") as f:
                for dict in dicts:
                    game=eval(dict)  
                    if game["Game Name"]!=self.name:
                        f.write(str(game)+"\n")
        with open("games.txt","a") as f:
                f.write(str(data)+"\n")
    
    def check(self,name):
        match=False
        with open("games.txt","r") as f:
            for line in f:
                save=eval(line)
                if save["Game Name"]==name:
                    match=True
        return match
            
    def leaderboard(self):
        def sorts(scores):
            return scores[1]
        print("User | High Score")
        scores=[]
        with open("games.txt","r") as f:
            for line in f:
                dicts=eval(line)
                data=dicts["Game Name"],dicts["High Score"]
                scores.append(tuple(data))
        scores.sort(key=sorts,reverse=True)    
        for item in scores:
            print(item[0],"|",item[1])

    def penalty(self):
        time.sleep(5)
        if self.guess==None and self.hard:
            print("Too Slow Point Reduction. Please enter input below and GET GUD U NOOB")
            self.hs=self.rpn.Start(self.hs,3,'-')
               
class RPNStack():
    def Start(self,hs,p,o):
        self.rpnstack=[]
        operators=['+','-']
        self.pointer=-1
        self.equa=[hs,p,o]
        for x in range(len(self.equa)):
            if str(self.equa[0]) in operators:
                v1=RPNStack.Pop(self)
                if self.equa[0]=='+':
                    return int(RPNStack.Peak(self))+int(v1)
                elif self.equa[0]=='-':
                    return int(RPNStack.Peak(self))-int(v1)
            elif str(self.equa[0]) not in operators:
                RPNStack.Append(self)
    def Append(self):
        self.pointer=self.pointer+1
        self.rpnstack.append(self.equa[0])
        self.equa.pop(0)                

    def Pop(self):
        pop=self.rpnstack[self.pointer]
        self.rpnstack.pop(self.pointer)
        self.pointer=self.pointer-1
        return pop
    
    def Peak(self):
        return self.rpnstack[self.pointer]
        
if __name__ == "__main__":
    Main()