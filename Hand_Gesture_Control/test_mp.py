
import mediapipe as mp
try:
    print(dir(mp))
    print("Solutions:", mp.solutions)
    print("Hands:", mp.solutions.hands)
except AttributeError as e:
    print(e)
