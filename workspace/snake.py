import turtle
import time
import random

# 设置屏幕
wn = turtle.Screen()
wn.title("贪吃蛇游戏")
wn.bgcolor("black")
wn.setup(width=600, height=600)
wn.tracer(0)  # 关闭自动更新

# 蛇头
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color("green")
head.penup()
head.goto(0, 0)
head.direction = "stop"

# 食物
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.goto(0, 100)

segments = []

# 分数
score = 0
high_score = 0

# 显示分数
pen = turtle.Turtle()
pen.speed(0)
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("分数: 0  最高分: 0", align="center", font=("Arial", 20, "normal"))

# 方向控制
def go_up():
    if head.direction != "down":
        head.direction = "up"

def go_down():
    if head.direction != "up":
        head.direction = "down"

def go_left():
    if head.direction != "right":
        head.direction = "left"

def go_right():
    if head.direction != "left":
        head.direction = "right"

wn.listen()
wn.onkeypress(go_up, "w")
wn.onkeypress(go_down, "s")
wn.onkeypress(go_left, "a")
wn.onkeypress(go_right, "d")
wn.onkeypress(go_up, "Up")
wn.onkeypress(go_down, "Down")
wn.onkeypress(go_left, "Left")
wn.onkeypress(go_right, "Right")

def move():
    if head.direction == "up":
        y = head.ycor()
        head.sety(y + 20)
    elif head.direction == "down":
        y = head.ycor()
        head.sety(y - 20)
    elif head.direction == "left":
        x = head.xcor()
        head.setx(x - 20)
    elif head.direction == "right":
        x = head.xcor()
        head.setx(x + 20)

# 游戏主循环
while True:
    wn.update()
    
    # 检查碰撞边界
    if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"
        
        # 隐藏蛇身
        for segment in segments:
            segment.goto(1000, 1000)
        segments.clear()
        
        score = 0
        pen.clear()
        pen.write(f"分数: {score}  最高分: {high_score}", align="center", font=("Arial", 20, "normal"))
    
    # 检查碰撞食物
    if head.distance(food) < 20:
        x = random.randint(-270, 270)
        y = random.randint(-270, 270)
        food.goto(x, y)
        
        new_segment = turtle.Turtle()
        new_segment.speed(0)
        new_segment.shape("square")
        new_segment.color("light green")
        new_segment.penup()
        segments.append(new_segment)
        
        score += 10
        if score > high_score:
            high_score = score
        
        pen.clear()
        pen.write(f"分数: {score}  最高分: {high_score}", align="center", font=("Arial", 20, "normal"))
    
    # 移动蛇身
    for i in range(len(segments) - 1, -1, -1):
        if i == 0:
            segments[i].goto(head.xcor(), head.ycor())
        else:
            segments[i].goto(segments[i-1].xcor(), segments[i-1].ycor())
    
    if segments:
        segments[0].goto(head.xcor(), head.ycor())
    
    move()
    
    # 检查蛇头碰撞蛇身
    for segment in segments:
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"
            
            for seg in segments:
                seg.goto(1000, 1000)
            segments.clear()
            
            score = 0
            pen.clear()
            pen.write(f"分数: {score}  最高分: {high_score}", align="center", font=("Arial", 20, "normal"))
    
    time.sleep(0.1)

wn.mainloop()