__author__ = 'ratcave'

from psychopy import event
import ratcave
from ratcave.graphics import *
import numpy as np
import argparse

np.set_printoptions(precision=2, suppress=True)

print('Importing MotivePy...')
import motive
motive.load_project('C:\\Users\\ratcave\\Desktop\\Motive Project 2015-10-15 12.30.12 AM.ttp')
motive.update()

def display(optitrack_ip="127.0.0.1", calib_object_name=''):

    # Connect to Optitrack
    # tracker = ratcave.devices.Optitrack(client_ip=optitrack_ip)

    # Create Arena and cube
    reader = WavefrontReader(ratcave.graphics.resources.obj_arena)
    arena = reader.get_mesh('Arena', lighting=True, centered=False)
    arena.load_texture(ratcave.graphics.resources.img_colorgrid)
    meshes = [arena]

    if calib_object_name:
        reader = WavefrontReader(ratcave.graphics.resources.obj_primitives)
        cube = reader.get_mesh('Sphere', lighting=True, scale=.02, centered=True)
        meshes.append(cube)

    # Create Scene and Window
    scene = Scene(meshes)
    scene.camera = projector
    scene.camera.fov_y = 27.8

    scene.light.position = scene.camera.position

    window = Window(scene, screen=1, fullscr=True)

    # Update Everything's Position

    # arena.world.position = tracker.rigid_bodies['Arena'].position
    # arena.world.rotation = tracker.rigid_bodies['Arena'].rotation_pca_y
    #
    print(motive.get_rigid_bodies())
    arena_rb = motive.get_rigid_bodies()['Arena']
    arena.world.position = arena_rb.location
    arena.world.rotation = arena_rb.rotation

    # Print the Following every time a key is detected:
    print "Camera settings:\n -shift: {0}, {1}\n -position: {2}\n -fov_y(xz): {3}\n -rotation: {4}\n\n".format(
        scene.camera.x_shift, scene.camera.y_shift, scene.camera.position, scene.camera.fov_y, scene.camera.rotation)
    print "Arena settings:\n -local\n\tPosition: {}\n\tRotation: {}\n -world\n\tPosition: {}\n\tRotation: {}".format(
        arena.local.position, arena.local.rotation, arena.world.position, arena.world.rotation)

    aa = 0
    arena_rb.reset_orientation()
    while True:

        # Update Everything's Position
        motive.update()

        arena.world.position = arena_rb.location
        arena.world.rotation = arena_rb.rotation_global

        # arena.world.position = tracker.rigid_bodies['Arena'].position
        # arena.world.rotation = tracker.rigid_bodies['Arena'].rotation_pca_y
        #aa += .5
        arena.world.rotation[1] += aa


        # If there's another object to track, then track it.
        if calib_object_name:
            # cube.local.position = tracker.rigid_bodies[calib_object_name].position
            cube.local.position = motive.get_rigid_bodies()[calib_object_name].location

        # Re-Draw Everything
        window.draw()
        window.flip()

        keys = event.getKeys()
        if 'escape' in keys:
            window.close()
            break
        elif 'up' in keys:
            scene.camera.fov_y += .1
            print('fov_y: {}'.format(scene.camera.fov_y))
        elif 'down' in keys:
            scene.camera.fov_y -= .1
            print('fov_y: {}'.format(scene.camera.fov_y))
        elif 'space' in keys:
            aa += 180



if __name__ == '__main__':

    # Get command line inputs
    parser = argparse.ArgumentParser(description="This displays an Optitrack Rigid Body called 'Arena' from the arena_scanner and opti_projector_calib stored coordinates.")
    parser.add_argument('-w',
                        action='store',
                        dest='calib_wand_name',
                        default='',
                        help="If a calibration wand or something is also trackable, then give the rigid body's name and a sphere will be placed in its position")
    args = parser.parse_args()

    display(calib_object_name=args.calib_wand_name)