import asyncio
import pygame
import sys
import random
pygame.init()
SCREEN_WIDTH=800
SCREEN_HEIGHT=600
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Trials and Trolls")
clock=pygame.time.Clock()
WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(220,50,50)
GREEN=(50,220,50)
BLUE=(50,100,220)
GRAY=(80,80,80)
YELLOW=(240,220,50)
PURPLE=(170,80,220)
font=pygame.font.Font(None,40)
small_font=pygame.font.Font(None,30)
large_font=pygame.font.Font(None,60)
ATTACK_NAMES={
    "Green Slime":["Bounced","Splashed","Body Slammed"],
    "Blue Slime":["Slapped","Splashed","Crushed"],
    "Fire Slime":["Burned","Scorched","Exploded"],
    "Magic Slime":["Spit Poison","Bit","Poison Burst"],
    "Minotaur Chief":["Charged","Gored","Crushed"],
    "Troll King":["Club Smash","Earthquake","Royal Slam"]
}
QUESTIONS={}
def generate_question_bank(difficulty,subject):
    ranges={"easy":(1,10),"normal":(5,25),"hard":(10,50),"very_hard":(20,100)}
    low,high=ranges[difficulty]
    bank=[]
    seen=set()
    while len(bank)<15:
        if subject=="addition":
            a=random.randint(low,high)
            b=random.randint(low,high)
            answer=a+b
            text=f"What is {a} + {b}?"
        elif subject=="multiplication":
            if difficulty=="very_hard":
                a=random.randint(6,15)
                b=random.randint(6,15)
            else:
                a=random.randint(max(2,low//2),max(3,high//3))
                b=random.randint(max(2,low//2),max(3,high//3))
            answer=a*b
            text=f"What is {a} × {b}?"
        elif subject=="division":
            divisor=random.randint(max(2,low//3),max(3,high//5))
            quotient=random.randint(max(2,low),max(4,high//2))
            dividend=divisor*quotient
            answer=quotient
            text=f"What is {dividend} ÷ {divisor}?"
        elif subject=="algebra":
            x=random.randint(max(2,low),max(5,high//2))
            a=random.randint(1,5 if difficulty in ["easy","normal"] else 10)
            b=random.randint(1,10 if difficulty=="easy" else 25)
            form=random.randint(0,2)
            if form==0:
                answer=x
                total=x+b
                text=f"x + {b} = {total}. What is x?"
            elif form==1:
                total=x-b
                if total<0:
                    total=x+b
                    text=f"x + {b} = {total}. What is x?"
                else:
                    answer=x
                    text=f"x - {b} = {total}. What is x?"
            else:
                answer=x
                total=a*x+b
                text=f"{a}x + {b} = {total}. What is x?"
        else:
            if difficulty=="easy":
                start_num=random.randint(1,10)
                step=random.randint(1,5)
                nums=[start_num+i*step for i in range(4)]
                answer=nums[-1]+step
            elif difficulty=="normal":
                start_num=random.randint(1,15)
                if random.choice([True,False]):
                    step=random.randint(2,8)
                    nums=[start_num+i*step for i in range(4)]
                    answer=nums[-1]+step
                else:
                    start_num=random.randint(1,5)
                    nums=[start_num*(2**i) for i in range(4)]
                    answer=nums[-1]*2
            elif difficulty=="hard":
                start_num=random.randint(2,10)
                if random.choice([True,False]):
                    step=random.randint(3,10)
                    nums=[start_num+i*step for i in range(4)]
                    answer=nums[-1]+step
                else:
                    nums=[start_num*(2**i) for i in range(4)]
                    answer=nums[-1]*2
            else:
                start_num=random.randint(2,10)
                if random.choice([True,False]):
                    multiplier=random.choice([2,3,4])
                    nums=[start_num*(multiplier**i) for i in range(4)]
                    answer=nums[-1]*multiplier
                else:
                    step=random.randint(10,30)
                    nums=[start_num+i*step for i in range(4)]
                    answer=nums[-1]+step
            text=f"{nums[0]}, {nums[1]}, {nums[2]}, {nums[3]}, ?"
        if text in seen:
            continue
        seen.add(text)
        choices={answer}
        spread=max(2,abs(answer)//5)
        while len(choices)<4:
            wrong=answer+random.randint(-spread,spread)
            if wrong!=answer and wrong>=0:
                choices.add(wrong)
        choices=list(choices)
        random.shuffle(choices)
        bank.append((text,[str(c) for c in choices],choices.index(answer)))
    return bank
def get_questions(difficulty,subject):
    if difficulty not in QUESTIONS:
        QUESTIONS[difficulty]={}
    if subject not in QUESTIONS[difficulty]:
        QUESTIONS[difficulty][subject]=generate_question_bank(difficulty,subject)
    return QUESTIONS[difficulty][subject]
class Button:
    def __init__(self,x,y,width,height,text):
        self.rect=pygame.Rect(x,y,width,height)
        self.text=text
    def draw(self,cooldown=0):
        color=GRAY if cooldown>0 else BLUE
        display_text=f"{self.text}\n{cooldown}" if cooldown>0 else self.text
        pygame.draw.rect(screen,color,self.rect)
        pygame.draw.rect(screen,WHITE,self.rect,3)
        lines=display_text.split("\n")
        start_y=self.rect.centery-(len(lines)*25)//2
        for i,line in enumerate(lines):
            text=small_font.render(line,True,WHITE)
            rect=text.get_rect(center=(self.rect.centerx,start_y+i*25))
            screen.blit(text,rect)
    def clicked(self,event):
        """Accept desktop mouse clicks and mobile touchscreen taps."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            return event.button == 1 and self.rect.collidepoint(event.pos)
        if event.type == pygame.FINGERDOWN:
            # Pygame finger coordinates are normalized to the range 0..1.
            x = int(event.x * SCREEN_WIDTH)
            y = int(event.y * SCREEN_HEIGHT)
            return self.rect.collidepoint(x, y)
        return False
class Character:
    def __init__(self,hp,strength,defense,image):
        self.max_hp=hp
        self.hp=hp
        self.strength=strength
        self.defense=defense
        self.image=image
        self.level=1
        self.experience=0
        self.experience_needed=100
        self.alive=True
        self.mastery={"addition":0,"multiplication":0,"division":0,"algebra":0,"patterns":0}
        self.correct=0
        self.wrong=0
    def attack(self,enemy,attack_name,bonus=1):
        damage_values={"Swing":35,"Spin":50,"Smash":70,"Headbutt":17}
        damage=damage_values[attack_name]
        final_damage=max(1,int(damage*self.strength/enemy.defense*bonus))
        enemy.hp=max(0,enemy.hp-final_damage)
        return final_damage
    def check_alive(self):
        if self.hp<=0:
            self.alive=False
class Enemy:
    def __init__(self,name,hp,strength,defense,xp,weak,medium,strong,image,subject):
        self.name=name
        self.max_hp=hp
        self.hp=hp
        self.strength=strength
        self.defense=defense
        self.experience_given=xp
        self.image=image
        self.weak_attack=weak
        self.medium_attack=medium
        self.strong_attack=strong
        self.subject=subject
        self.alive=True
    def attack(self,player):
        damage=random.choice([self.weak_attack,self.medium_attack,self.strong_attack])
        final_damage=max(1,damage*self.strength//player.defense)
        player.hp=max(0,player.hp-final_damage)
        return final_damage
    def check_alive(self):
        if self.hp<=0:
            self.alive=False
def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        surface=pygame.Surface((120,120))
        surface.fill(GRAY)
        return surface
player=Character(120,2,2,load_image("images/Knight(128).png"))
encounter=0
def make_enemy(number):
    enemies=[
        Enemy("Green Slime",100,2,3,100,4,8,12,load_image("images/Green Slime.png"),"addition"),
        Enemy("Blue Slime",140,3,4,150,6,12,18,load_image("images/Blue Slime.png"),"multiplication"),
        Enemy("Fire Slime",170,3,4,180,7,12,18,load_image("images/Fire Slime.png"),"division"),
        Enemy("Magic Slime",210,4,5,220,8,15,22,load_image("images/Magic Slime.png"),"algebra"),
        Enemy("Minotaur Chief",240,4,5,350,8,15,22,load_image("images/Minotaur Chief(175).png"),"patterns"),
        Enemy("Troll King",350,5,6,700,10,20,28,load_image("images/Troll King(175).png"),"algebra")
    ]
    return enemies[number]
slime=make_enemy(encounter)
intro_continue_button=Button(300,450,200,60,"Continue")
victory_continue_button=Button(300,400,200,60,"Continue")
restart_button=Button(300,450,200,60,"Restart")
swing_button=Button(50,470,150,60,"Swing")
spin_button=Button(220,470,150,60,"Spin")
smash_button=Button(390,470,150,60,"Smash")
headbutt_button=Button(560,470,170,60,"Headbutt")
heal_button=Button(50,400,150,60,"Heal")
answer_buttons=[Button(80,350,280,70,""),Button(440,350,280,70,""),Button(80,440,280,70,""),Button(440,440,280,70,"")]
hp_button=Button(100,470,180,60,"HP +60")
strength_button=Button(310,470,180,60,"Strength +2")
defense_button=Button(520,470,180,60,"Defense +2")
game_state="INTRO"
battle_over=False
winner=""
message="Choose an attack!"
level_message=""
question=None
question_choices=[]
question_answer=0
question_subject=""
selected_attack=""
question_message=""
question_locked=False
question_start_time=0
QUESTION_TIME_LIMIT=10
attack_cooldowns={"Swing":0,"Spin":0,"Smash":0,"Headbutt":0,"Heal":0}
def draw_text(text,x,y,color=WHITE,size="normal"):
    if size=="large":
        surface=large_font.render(text,True,color)
    elif size=="small":
        surface=small_font.render(text,True,color)
    else:
        surface=font.render(text,True,color)
    screen.blit(surface,(x,y))
def draw_hp_bar(x,y,current_hp,max_hp,color):
    width=250
    height=25
    pygame.draw.rect(screen,GRAY,(x,y,width,height))
    health=int(width*max(0,current_hp)/max_hp)
    pygame.draw.rect(screen,color,(x,y,health,height))
    pygame.draw.rect(screen,WHITE,(x,y,width,height),3)
def draw_health():
    draw_text("PLAYER",50,20)
    draw_hp_bar(50,55,player.hp,player.max_hp,GREEN)
    draw_text(f"{player.hp}/{player.max_hp}",130,90,size="small")
    draw_text(f"LV {player.level}",50,125,YELLOW,"small")
    draw_text(slime.name.upper(),470,20,RED)
    draw_hp_bar(500,55,slime.hp,slime.max_hp,RED)
    draw_text(f"{slime.hp}/{slime.max_hp}",580,90,size="small")
def draw_intro():
    screen.fill(BLACK)
    draw_text("Trials and Trolls",250,50,RED,"large")
    lines=["You leave your hometown seeking adventure.","But the monsters guarding the kingdom","have a strange power...","They force you to THINK before you can win."]
    y=150
    for line in lines:
        draw_text(line,70,y,size="small")
        y+=45
    draw_text("Defeat monsters by solving problems.",130,350,YELLOW)
    intro_continue_button.draw()
def draw_battle():
    screen.fill(BLACK)
    draw_health()
    screen.blit(player.image,(150,250))
    screen.blit(slime.image,(550,150))
    draw_text(f"{slime.name} blocks your path!",180,150,YELLOW)
    lines=message.split("\n")[-3:]
    y=190
    for line in lines:
        draw_text(line,80,y,size="small")
        y+=35
    if not battle_over:
        swing_button.draw(attack_cooldowns["Swing"])
        spin_button.draw(attack_cooldowns["Spin"])
        smash_button.draw(attack_cooldowns["Smash"])
        headbutt_button.draw(attack_cooldowns["Headbutt"])
        heal_button.draw(attack_cooldowns["Heal"])
        draw_text("Normal",82,535,YELLOW,"small")
        draw_text("Hard",270,535,YELLOW,"small")
        draw_text("Very Hard",418,535,YELLOW,"small")
        draw_text("Easy",620,535,YELLOW,"small")
    elif winner=="PLAYER":
        draw_text("VICTORY!",300,350,GREEN)
        victory_continue_button.draw()
def draw_question():
    screen.fill(BLACK)
    draw_text("KNOWLEDGE TRIAL",235,40,PURPLE,"large")
    draw_text(f"Topic: {question_subject.upper()}",300,105,YELLOW,"small")
    draw_text(f"Attack: {selected_attack}",300,135,WHITE,"small")
    elapsed=(pygame.time.get_ticks()-question_start_time)/1000
    remaining=max(0,QUESTION_TIME_LIMIT-elapsed)
    timer_color=RED if remaining<=3 else YELLOW
    draw_text(f"TIME: {remaining:.1f}",330,165,timer_color,"small")
    draw_text(question,100,205)
    draw_text("Answer correctly to land your attack!",180,265,GREEN,"small")
    for i,button in enumerate(answer_buttons):
        button.text=question_choices[i]
        button.draw()
    if question_message:
        draw_text(question_message,180,540,YELLOW,"small")
def draw_levelup():
    screen.fill(BLACK)
    draw_text("LEVEL UP!",280,50,YELLOW,"large")
    draw_text(level_message,120,130)
    draw_text(f"Level: {player.level}",100,190,WHITE,"small")
    draw_text(f"HP: {player.max_hp}",100,225,GREEN,"small")
    draw_text(f"Strength: {player.strength}",300,225,RED,"small")
    draw_text(f"Defense: {player.defense}",500,225,BLUE,"small")
    draw_text("Choose your upgrade:",270,320,WHITE,"small")
    hp_button.draw()
    strength_button.draw()
    defense_button.draw()
def draw_gameover():
    screen.fill(BLACK)
    if encounter>=6:
        draw_text("YOU DEFEATED THE TROLL KING!",120,120,GREEN,"large")
        draw_text("You mastered the trials.",230,220,YELLOW)
        draw_text(f"Questions correct: {player.correct}",230,290)
        draw_text(f"Questions wrong: {player.wrong}",230,330)
    else:
        draw_text("GAME OVER",250,150,RED,"large")
        draw_text(f"Questions correct: {player.correct}",230,250)
        draw_text(f"Questions wrong: {player.wrong}",230,290)
    restart_button.draw()
def reset_cooldowns():
    for attack in attack_cooldowns:
        attack_cooldowns[attack]=0
def reduce_cooldowns():
    for attack in attack_cooldowns:
        if attack_cooldowns[attack]>0:
            attack_cooldowns[attack]-=1
def level_up():
    global level_message
    leveled=False
    while player.experience>=player.experience_needed:
        player.experience-=player.experience_needed
        player.level+=1
        player.experience_needed*=2
        leveled=True
    if leveled:
        level_message=f"You reached level {player.level}!"
    return leveled
def get_question_difficulty(attack):
    if attack=="Headbutt":
        return "easy"
    if attack=="Swing":
        return "normal"
    if attack=="Spin":
        return "hard"
    if attack=="Smash":
        return "very_hard"
def create_question(subject,attack):
    global question,question_choices,question_answer,question_subject,question_message,question_locked,question_start_time
    question_subject=subject
    difficulty=get_question_difficulty(attack)
    question,choices,correct_index=random.choice(get_questions(difficulty,subject))
    correct_answer=choices[correct_index]
    question_choices=choices.copy()
    random.shuffle(question_choices)
    question_answer=question_choices.index(correct_answer)
    question_message=""
    question_locked=False
    question_start_time=pygame.time.get_ticks()
def start_attack(move):
    global selected_attack,game_state
    if attack_cooldowns[move]>0:
        return
    selected_attack=move
    create_question(slime.subject,move)
    game_state="QUESTION"
def enemy_counterattack():
    global message,battle_over,winner,game_state
    enemy_damage=slime.attack(player)
    attack_name=random.choice(ATTACK_NAMES[slime.name])
    message+=f"\n{slime.name} used {attack_name} and dealt {enemy_damage} damage!"
    player.check_alive()
    if not player.alive:
        battle_over=True
        winner="SLIME"
        game_state="GAMEOVER"
        message=f"The {slime.name} defeated you..."
def question_time_expired():
    return (pygame.time.get_ticks()-question_start_time)>=QUESTION_TIME_LIMIT*1000
def answer_question(index):
    global question_message,question_locked,game_state,message
    if question_locked:
        return
    if question_time_expired():
        question_locked=True
        player.wrong+=1
        player.mastery[question_subject]=max(0,player.mastery[question_subject]-1)
        question_message="TIME'S UP! Your attack failed!"
        message=f"You ran out of time on your {selected_attack}!"
        enemy_counterattack()
        if game_state!="GAMEOVER":
            game_state="BATTLE"
        return
    question_locked=True
    if index==question_answer:
        player.correct+=1
        player.mastery[question_subject]+=1
        question_message="CORRECT! Attack successful!"
        perform_attack(selected_attack)
    else:
        player.wrong+=1
        player.mastery[question_subject]=max(0,player.mastery[question_subject]-1)
        question_message="WRONG! Your attack failed!"
        message=f"You missed your {selected_attack}!"
        enemy_counterattack()
    if game_state!="GAMEOVER":
        game_state="BATTLE"
def perform_attack(move):
    global message,battle_over,winner,encounter
    damage=player.attack(slime,move,1.5)
    message=f"You used {move} and dealt {damage} damage!"
    cooldowns={"Swing":2,"Spin":3,"Smash":5,"Headbutt":0}
    attack_cooldowns[move]=cooldowns[move]
    reduce_cooldowns()
    slime.check_alive()
    if not slime.alive:
        player.experience+=slime.experience_given
        player.hp=min(player.max_hp,player.hp+60)
        battle_over=True
        winner="PLAYER"
        message+=f"\nYou defeated the {slime.name}!"
        message+="\nYou recovered 60 HP!"
        encounter+=1
        return
    enemy_counterattack()
def player_heal():
    global message
    if attack_cooldowns["Heal"]>0:
        message="Heal is on cooldown!"
        return
    heal_amount=int(player.max_hp/4)
    old_hp=player.hp
    player.hp=min(player.max_hp,player.hp+heal_amount)
    healed=player.hp-old_hp
    attack_cooldowns["Heal"]=2
    reduce_cooldowns()
    message=f"You healed for {healed} HP!"
    enemy_counterattack()
def next_enemy():
    global slime,battle_over,winner,message,game_state
    if encounter>=6:
        game_state="GAMEOVER"
        return
    slime=make_enemy(encounter)
    battle_over=False
    winner=""
    reset_cooldowns()
    message=f"A {slime.name} appears!"
    game_state="BATTLE"
def restart_game():
    global player,slime,encounter,battle_over,winner,message,game_state,QUESTIONS
    player=Character(120,2,2,load_image("images/Knight(128).png"))
    encounter=0
    slime=make_enemy(encounter)
    battle_over=False
    winner=""
    message="Choose an attack!"
    reset_cooldowns()
    QUESTIONS={}
    game_state="INTRO"
async def main():
    global game_state, message, player
    running=True
    while running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            if game_state=="INTRO":
                if intro_continue_button.clicked(event):
                    game_state="BATTLE"
                    message="Choose an attack!"
            elif game_state=="BATTLE":
                if not battle_over:
                    if swing_button.clicked(event):
                        start_attack("Swing")
                    elif spin_button.clicked(event):
                        start_attack("Spin")
                    elif smash_button.clicked(event):
                        start_attack("Smash")
                    elif headbutt_button.clicked(event):
                        start_attack("Headbutt")
                    elif heal_button.clicked(event):
                        player_heal()
                elif winner=="PLAYER":
                    if victory_continue_button.clicked(event):
                        if encounter>=6:
                            game_state="GAMEOVER"
                        elif level_up():
                            game_state="LEVELUP"
                        else:
                            next_enemy()
            elif game_state=="QUESTION":
                if question_time_expired() and not question_locked:
                    answer_question(-1)
                elif not question_locked:
                    for i,button in enumerate(answer_buttons):
                        if button.clicked(event):
                            answer_question(i)
            elif game_state=="LEVELUP":
                if hp_button.clicked(event):
                    player.max_hp+=60
                    player.hp=player.max_hp
                    next_enemy()
                elif strength_button.clicked(event):
                    player.strength+=2
                    player.hp=player.max_hp
                    next_enemy()
                elif defense_button.clicked(event):
                    player.defense+=2
                    player.hp=player.max_hp
                    next_enemy()
            elif game_state=="GAMEOVER":
                if restart_button.clicked(event):
                    restart_game()
        if game_state=="QUESTION" and not question_locked and question_time_expired():
            answer_question(-1)
        if game_state=="INTRO":
            draw_intro()
        elif game_state=="BATTLE":
            draw_battle()
        elif game_state=="QUESTION":
            draw_question()
        elif game_state=="LEVELUP":
            draw_levelup()
        elif game_state=="GAMEOVER":
            draw_gameover()
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    pygame.quit()

asyncio.run(main())
