#
#	Global configuration for SNAP makefiles
#
PROGS = eventrate eventratemaster threadrate updown-dram-readbw updown-dram-writebw
GLIB = glib-core
SNAP = snap-core
GLIBADV = glib-adv
SNAPADV = snap-adv
SNAPEXP = snap-exp

CGLIB = ../../$(GLIB)
CSNAP = ../../$(SNAP)

EXGLIB = ../../$(GLIB)
EXSNAP = ../../$(SNAP)
EXGLIBADV = ../../$(GLIBADV)
EXSNAPADV = ../../$(SNAPADV)
EXSNAPEXP = ../../$(SNAPEXP)

CC = g++
CXXFLAGS += -std=c++98 -Wall -std=c++11
CXXFLAGS += -O3 -DNDEBUG -fopenmp
# turn on for crash debugging, get symbols with <prog> 2>&1 | c++filt
#CXXFLAGS += -g -rdynamic
#CXXFLAGS += -ggdb
# turn on for OpenMP
CXXOPENMP = 
LDFLAGS += -I../../../../../../include -L../../../../../../util/m5/build/x86/out
LIBS += -lrt -lm5

#LIBS += -lrt #-lm5

all: $(PROGS) 

# COMPILE
eventrate: eventrate.cpp $(DEPH) $(DEPCPP) $(EXSNAP)/Snap.o 
	$(CC) $(CXXFLAGS) -o $@ $< $(DEPCPP) $(EXSNAP)/Snap.o -I$(EXSNAP) -I$(EXSNAPADV) -I$(EXGLIB) -I$(EXSNAPEXP) $(LDFLAGS) $(LIBS)  
eventratemaster: eventratemaster.cpp $(DEPH) $(DEPCPP) $(EXSNAP)/Snap.o 
	$(CC) $(CXXFLAGS) -o $@ $< $(DEPCPP) $(EXSNAP)/Snap.o -I$(EXSNAP) -I$(EXSNAPADV) -I$(EXGLIB) -I$(EXSNAPEXP) $(LDFLAGS) $(LIBS)  
threadrate: threadrate.cpp $(DEPH) $(DEPCPP) $(EXSNAP)/Snap.o 
	$(CC) $(CXXFLAGS) -o $@ $< $(DEPCPP) $(EXSNAP)/Snap.o -I$(EXSNAP) -I$(EXSNAPADV) -I$(EXGLIB) -I$(EXSNAPEXP) $(LDFLAGS) $(LIBS)  
updown-dram-readbw: updown-dram-readbw.cpp $(DEPH) $(DEPCPP) $(EXSNAP)/Snap.o 
	$(CC) $(CXXFLAGS) -o $@ $< $(DEPCPP) $(EXSNAP)/Snap.o -I$(EXSNAP) -I$(EXSNAPADV) -I$(EXGLIB) -I$(EXSNAPEXP) $(LDFLAGS) $(LIBS)  
updown-dram-writebw: updown-dram-writebw.cpp $(DEPH) $(DEPCPP) $(EXSNAP)/Snap.o 
	$(CC) $(CXXFLAGS) -o $@ $< $(DEPCPP) $(EXSNAP)/Snap.o -I$(EXSNAP) -I$(EXSNAPADV) -I$(EXGLIB) -I$(EXSNAPEXP) $(LDFLAGS) $(LIBS)  
#$(EXSNAP)/Snap.o: 
#	make -C $(EXSNAP)

clean:
	rm -f *.o  $(PROGS)  $(PROGS).exe
	rm -rf ../../bin/*
