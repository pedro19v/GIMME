INCLUDES= \
-I ./source/Adaptation/AlgDefStructs/ \
-I ./source/Adaptation/ \
-I ./source/AuxStructs/ \
-I ./source/Player/

CPPFiles = \
./source/GIMMECore.cpp \
./source/Adaptation/AlgDefStructs/*.cpp \
./source/Adaptation/*.cpp \
./source/AuxStructs/*.cpp \
./source/Player/*.cpp

GIMMECore: 
	g++ -c -fPIC $(INCLUDES) $(CPPFiles)
	g++ -shared -Wl,-soname,GIMMECore.so -o GIMMECore.so  *.o
clean:
	rm -f *.o
