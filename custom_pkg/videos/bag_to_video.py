import cv2
from rosbags.highlevel import AnyReader
from rosbags.image import message_to_cvimage
from rosbags.typesys import Stores

# === CONFIG ===
bag_path = '/home/ainhoaarnaiz/my_zed_bag/video_test'  # Change this
image_topic = '/zed/zed_node/left/image_rect_color'
output_video_path = 'output.mp4'
fps = 15  # You can adjust this

# === READ BAG ===
with AnyReader([bag_path]) as reader:
    reader.open()

    # Find the image topic connection
    connection = next((c for c in reader.connections if c.topic == image_topic), None)
    if not connection:
        raise RuntimeError(f"Topic '{image_topic}' not found in bag.")

    # Get messages
    messages = list(reader.messages(connections=[connection]))

    # Decode the first image to get frame size
    first_msg = messages[0][1]
    frame = message_to_cvimage(first_msg, Stores.msgtype(connection.msgtype))
    height, width = frame.shape[:2]

    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    # Loop through messages and write frames
    for _, msg, _ in messages:
        img = message_to_cvimage(msg, Stores.msgtype(connection.msgtype))
        if img.ndim == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        out.write(img)

    out.release()
    print(f"Saved video to: {output_video_path}")
