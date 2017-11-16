CC = g++
CFLAGS = 
LIBS = -std=c++11

% : %.cpp
	$(CC) -o $@ $< $(CFLAGS) $(LIBS)
