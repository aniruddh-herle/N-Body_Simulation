import numpy as np
import time
import imageio
import matplotlib.pyplot as plt
import os
from natsort import natsorted

def calc_acc( pos, mass, G, softening ):
	"""
    This block calculates the acceleration of each particle using Newton's Law 
    pos  is an N x 3 matrix of positions
	mass is an N x 1 vector of masses
	G is Newton's Gravitational constant
	softening is the softening length
	a is N x 3 matrix of accelerations
	"""
	# positions r = [x,y,z] for all particles
	x = pos[:,0:1]
	y = pos[:,1:2]
	z = pos[:,2:3]

	# matrix that stores all pairwise particle separations: r_j - r_i
	dx = x.T - x
	dy = y.T - y
	dz = z.T - z

	# matrix that stores 1/r^3 for all particle pairwise particle separations 
	inv_r3 = (dx**2 + dy**2 + dz**2 + softening**2)
	inv_r3[inv_r3>0] = inv_r3[inv_r3>0]**(-1.5)

	ax = G * (dx * inv_r3) @ mass
	ay = G * (dy * inv_r3) @ mass
	az = G * (dz * inv_r3) @ mass
	
	# pack together the acceleration components
	a = np.hstack((ax,ay,az))

	return a

def main():
  """ N-body simulation """
    
  # Simulation parameters
  N         = 100    # Number of particles
  t         = 0      # current time of the simulation
  tEnd      = 10.0   # time at which simulation ends
  dt        = 0.01   # timestep
  softening = 0.1    # softening length
  G         = 1.0    # Newton's Gravitational Constant
  plotRealTime = True # switch on for plotting as the simulation goes along
    
  # Generate Initial Conditions
  np.random.seed(17)            # set the random number generator seed
    
  mass = 20.0*np.ones((N,1))/N  # total mass of particles is 20
  pos  = np.random.randn(N,3)   # randomly selected positions and velocities
  vel  = np.random.randn(N,3)
    
  # Convert to Center-of-Mass frame
  vel -= np.mean(mass * vel,0) / np.mean(mass)
    
  # calculate initial gravitational accelerations
  acc = calc_acc( pos, mass, G, softening )
        
  # number of timesteps
  Nt = int(np.ceil(tEnd/dt))
    
  # save energies, particle orbits for plotting trails
  pos_save = np.zeros((N,3,Nt+1))
  pos_save[:,:,0] = pos
  
  t_all = np.arange(Nt+1)*dt
    
  # prep figure
  fig = plt.figure(figsize=(10,10), dpi=80)
  grid = plt.GridSpec(3, 1, wspace=0.0, hspace=0.3)
  ax1 = plt.subplot(grid[0:2,0])
  
  # Simulation Main Loop
  for i in range(Nt):
    # (1/2) kick
    vel += acc * dt/2.0
        
    # drift
    pos += vel * dt
        
    # update accelerations
    acc = calc_acc( pos, mass, G, softening )
        
    # (1/2) kick
    vel += acc * dt/2.0
        
    # update time
    t += dt
        
    # save energies, positions for plotting trail
    pos_save[:,:,i+1] = pos
         
      
    # plot in real time
    if plotRealTime or (i == Nt-1):
          
      plt.sca(ax1)
      plt.cla()
      xx = pos_save[:,0,max(i-50,0):i+1]
      yy = pos_save[:,1,max(i-50,0):i+1]
      plt.scatter(xx,yy,s=1,color=[.7,.7,1])
      plt.scatter(pos[:,0],pos[:,1],s=10,color='black')
      ax1.set(xlim=(-2, 2), ylim=(-2, 2))
      ax1.set_aspect('equal', 'box')
      ax1.set_xticks([-2,-1,0,1,2])
      ax1.set_yticks([-2,-1,0,1,2])
      plt.savefig('images/'+str(i)+'.png')
           
         
 
  plt.show()
      
  return 0

#create a folder called 'images' to store the individual plots. They will later be converted into an animation
start=time.time()
main()
stop=time.time()
print(f"Total Simulation time is {(stop-start)/60} mins")

#This saves the plots as an animation. The individual plots are saved and then converted into a video.

path='images/'
fileList = []
for file in os.listdir(path):
    
        complete_path = path + file
        fileList.append(complete_path)
fileList=natsorted(fileList)

writer = imageio.get_writer('video1.mp4', fps=20)

for im in fileList:
    writer.append_data(imageio.imread(im))
writer.close()
