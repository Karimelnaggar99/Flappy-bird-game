import pygame
import neat
import time
import os
import random
import pygame.font

WIN_WIDTH=500
WIN_HEIGHT=800
BLACK=(0,0,0)

BIRD_IMGS=[pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))),pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG=pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bg.png")))

class Bird:
    IMGS=BIRD_IMGS
    MAX_ROTATION=25
    ROT_VEL= 20
    ANIMATION_TIME= 5

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count=0
        self.vel=0
        self.height=self.y
        self.img_count=0
        self.img=self.IMGS[0]
    
    def jump(self):
        self.vel=-10.5 #to move up you need negative value
        self.tick_count=0 #track when we last jumped
        self.height=self.y #track where the bird jumped from
    
    def move(self):
        self.tick_count +=1 #a frame went by, how much we moved

        d=self.vel*self.tick_count+1.5*self.tick_count**2 #calculate how much we moved up, ex: -10.5+1.5=-9

        if d >= 16:
            d=16
        if d < 0:
            d-=2
        self.y = self.y +d

        if d <0 or self.y<self.height+50:
            if self.tilt<self.MAX_ROTATION:#make sure bird doesnt over tilt
                self.tilt=self.MAX_ROTATION
        else:
            if self.tilt>-90:
                self.tilt-=self.ROT_VEL
    
    def draw(self,win):
        self.img_count+=1
        #transition bird between images
        if self.img_count < self.ANIMATION_TIME:
            self.img=self.IMGS[0]
        elif self.img_count< self.ANIMATION_TIME*2:
            self.img=self.IMGS[1]
        elif self.img_count< self.ANIMATION_TIME*3:
            self.img=self.IMGS[2]
        elif self.img_count< self.ANIMATION_TIME*4:
            self.img=self.IMGS[1]
        elif self.img_count< self.ANIMATION_TIME*4 + 1:
            self.img=self.IMGS[0]
            self.img_count= 0
        if self.tilt <=-80:#make sure when tilted down and falling the wings are closed
            self.img=self.IMGS[1]
            self.img_count=self.ANIMATION_TIME*2           

        rotated_image=pygame.transform.rotate(self.img,self.tilt)
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
        win.blit(rotated_image,new_rect.topleft)
    
    def get_mask(self):#pixel perfect collision
        return pygame.mask.from_surface(self.img)


class Pipe:
    Gap=200
    VEL=5

    def __init__(self,x):
        self.x=x
        self.height=0
        self.top=0
        self.bottom=0
        self.PIPE_TOP= pygame.transform.flip(PIPE_IMG,False,True)
        self.PIPE_BOTTOM= PIPE_IMG

        self.passed = False
        self.set_height()
    
    def set_height(self):
        self.height=random.randrange(50,450)
        self.top=self.height - self.PIPE_TOP.get_height()
        self.bottom=self.height + self.Gap

    def move(self):
        self.x-=self.VEL
    
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))
    
    def collide(self,bird):
        bird_mask=bird.get_mask()
        top_mask=pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x-bird.x,self.top-round(bird.y))
        bottom_offset=(self.x-bird.x,self.bottom-round(bird.y))
        b_point= bird_mask.overlap(bottom_mask,bottom_offset)
        t_point= bird_mask.overlap(top_mask,top_offset)
        if t_point or b_point:
            return True
        return False


class Base:
    VEL=5
    WIDTH=BASE_IMG.get_width()
    IMG=BASE_IMG
    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH
    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL
        if self.x1 + self.WIDTH <0:#we draw 2 bases, and when one base gets out of screen we cycle it to the back
            self.x1=self.x2+self.WIDTH
        if self.x2 +self.WIDTH <0:
            self.x2=self.x1 +self.WIDTH
    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))




def draw_window(win, bird,pipes,base):
    win.blit(BG_IMG,(0,0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    bird.draw(win)
    pygame.display.update()

def display_score(score,win):
    pygame.font.init()

    score_Text= pygame.font.SysFont('Comic Sans MS',50).render(f"Score: {score}",True,BLACK)
    win.blit(score_Text,(10,10))

# def display_lose(win):
#     pygame.font.init()
#     lose_Text= pygame.font.SysFont('Comic Sans MS',50).render("Great Job Potato!",True,BLACK)
#     win.blit(lose_Text,(20,20))


def main():
    bird=Bird(230,250)
    base=Base(630)
    pipes=[Pipe(600)]
    win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))
    clock=pygame.time.Clock()
    run=True
    score =0
    clock = pygame.time.Clock()
    # pygame.init()
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run=False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                bird.jump()
                print("Spacebar pressed")
        bird.move()
        
        rem=[]
        add_pipe=False
        for pipe in pipes:
            if pipe.collide(bird):
                run=False
            if pipe.x + pipe.PIPE_TOP.get_width()<0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed=True
                add_pipe=True
            pipe.move()
        if add_pipe:
            score+=1
            pipes.append(Pipe(600))
        display_score(score,win)
        pygame.display.flip()
        for r in rem:
            pipes.remove(r)
        if bird.y + bird.img.get_height() >= 630:#bird hits the floor
            run = False

        base.move()
        draw_window(win,bird,pipes,base)
    
    pygame.time.wait(3000)
    
    pygame.quit()
    quit()

main()

