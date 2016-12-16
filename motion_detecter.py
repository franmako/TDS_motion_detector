import argparse
import imutils
import cv2

# argument parser : sert a passer une video ou utiliser webcam
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="path to the video file")
ap.add_argument("-a", "--min-area", type=int, default=2000, help="minimum area size")
args = vars(ap.parse_args())

if args.get("video", None) is None:
	camera = cv2.VideoCapture(0)
	time.sleep(0.25)
else:
	camera = cv2.VideoCapture(args["video"])

# la premiere image est utilise pour comparer les autres
firstFrame = None

while True:
	#on initialise le compteur et on prend la premiere image
	(grabbed, frame) = camera.read()
	people = 0

	# si on ne sait plus prendre d'image, alors c'est la fin du flux
	if not grabbed:
		break

	# on reduit la taille pour avoir de meilleures performances
	frame = imutils.resize(frame, width=500)
	# on convertit l'image en noir/blanc, facilite la comparaison
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	# on floute l'image pour trouver les contours plus facilement
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	# on initialise la premiere image
	if firstFrame is None:
		firstFrame = gray
		continue

    # on calcule les changements entre la premiere image et le suivant
	frameDelta = cv2.absdiff(firstFrame, gray)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	# on dilate pour remplir les trous
	thresh = cv2.dilate(thresh, None, iterations=2)
	(cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)

	# on cree les contours
	for c in cnts:
		# si le contour est trop petit, on l'ignore
		if cv2.contourArea(c) < args["min_area"]:
			continue

		# on dessine le contour sur la video
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		# on incremente, a chaque fois qu'on dessine des contours
		people = people + 1

        # draw the text and timestamp on the frame
	cv2.putText(frame, "Personnes dans la salle d'attente: {}".format(people), (10, 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

	# on affiche la video
	cv2.imshow("Salle d'attente - Camera", frame)
	#cv2.imshow("Thresh", thresh)
	#cv2.imshow("Frame Delta", frameDelta)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key is pressed, break from the lop
	if key == ord("q"):
		break

# cleanup the camera and close any open windows
camera.release()
cv2.destroyAllWindows()
