#pragma once

// 2020-11-02
#include<sys/select.h>
#include<unistd.h>
// 2020-11-02
#include<stdio.h>
#include<sys/time.h>
#include<time.h>
// 2021-01-05

struct InputKeyboardXlib {
  Input& input;
  InputKeyboardXlib(Input& input) : input(input) {}

  shared_pointer<HID::Keyboard> hid{new HID::Keyboard};

  Display* display = nullptr;

  struct Key {
    string name;
    uint keysym;
    uint keycode;
  };
  vector<Key> keys;

  //2021-01-05
  struct timeval tvalBefore, tvalAfter;
  char buff_time[70];  
  // 2020-11-02
  double final_time_calc = 0.0;
  FILE *file_keypresser;
  time_t epoch_time;
  struct tm ts;
  char filepath_name[300];
  char file_name[5000];
  uint simulate_keypress_flag               = 0;
  uint simulate_keypress_flag_one           = 0;
  uint simulate_keypress_flag_two           = 0;
  uint simulate_keypress_flag_three         = 0;
  uint simulate_keypress_flag_four          = 0;
  uint simulate_keypress_flag_five          = 0;
  uint simulate_keypress_flag_six           = 0;
  uint implement_simulated_keypresses       = 0;
  uint implement_slow_frame_rate            = 0;
  useconds_t slow_frame_rate_sleep_interval = 0;
  int  fd;                                 // file descriptor, not FILE * pointer
  //uint timer                                = 0; //timer for the slowdown toggle
  #define MAX_BUFFER_SIZE 100
  auto select_poll() -> void {
    //strucnt timeval timeout = {0, 100 * 1000};
    struct timeval timeout;
    int    count;
    fd_set rfd;
    char   buffer[MAX_BUFFER_SIZE + 1];

    //printf("select_poll(): flag is %d\n", implement_simulated_keypresses);
    if (! implement_simulated_keypresses) { return; }

    // slow the frame rate as needed but only after the first 'a' is seen.
    // otherwise the game takes forever to load.
    // interval 100 msec (100000 usec) yields about 9 fps, 50 msec yields 14 fps.
    if (2 == implement_slow_frame_rate) {
       usleep(slow_frame_rate_sleep_interval);
    }
    
    FD_ZERO( &rfd );
    FD_SET ( fd, &rfd );
    // zero timeout returns immediately whether or not input is available so it's useful for polling
    timeout.tv_sec  = 0;
    timeout.tv_usec = 0;
    memset(buffer, 0, MAX_BUFFER_SIZE);
    count = read(fd, buffer, MAX_BUFFER_SIZE);
    printf("%s", &buffer[0]);
    char *cp = &buffer[0];
    count = 0;
    //Possible Buffer overflow or write here
    while ((*cp != 0) && (cp < buffer + MAX_BUFFER_SIZE)){
      //printf("This is what is in the buffer %c \n", *cp);

      if(*cp == 'a'){
	simulate_keypress_flag += 1;
	
      }
      //This is for the slowdown factor
      else if(*cp == '1'){
	simulate_keypress_flag_one += 1;
      }
      else if(*cp == '2'){
	simulate_keypress_flag_two += 1;
      }
      
      //directional controls
      else if(*cp == 'u'){
	simulate_keypress_flag_three += 1;
      }
      else if(*cp == 'd'){
	simulate_keypress_flag_four += 1;
      }

      else if(*cp == 'l'){
	simulate_keypress_flag_five += 1;
      }
      else if(*cp == 'r'){
	simulate_keypress_flag_six += 1;
      }
      
      
      cp++;
    }
    
    //2021-01-11: fixed simulate flag to simulate 'a', '1' and '2' as well as read the buffer for content
    //count = select(fd + 1, &rfd, NULL, NULL, &timeout);
    //if (FD_ISSET(fd, &rfd)) {
    // printf("select_poll(): fd %d is set and select count is %d\n", fd, count);
      // try to read all the characters in the buffer, which we
      // assume will be the same character. In case they are repeated,
      // we can issue repeated simulated keypresses.  We will add
      // the new total to the ones received earlier in case that proves useful.
      // read returns the number of bytes read.
      // count                   = read(fd, &buffer, MAX_BUFFER_SIZE);
      // simulate_keypress_flag += count;
      // if (count > 0) {
      //   printf("select_poll(): read %d, so new value of simulate_keypress_flag is %d\n", count, simulate_keypress_flag);
      // }
      //}
  }

  auto select_setup() -> void {
     // open input file (or socket)
     char buffer[1000];  // sigh. Avoids having to malloc storage
     char cwd[900];     // sigh. Avoids having to malloc storage
     FILE *fp;

     getcwd(cwd, 899);
     sprintf(buffer, "%s/myfifo", cwd);
     // sprintf(buffer, "%s/byuu.simulated_keypresses.txt", cwd);
     printf("select_setup(): fixing to open input pipe with '%s' (len %d)\n", buffer, int(strlen(buffer)));
     // thanks to https://stackoverflow.com/questions/8507810/why-does-my-program-hang-when-opening-a-mkfifo-ed-pipe
     if(( fd = open( buffer, O_RDONLY | O_NONBLOCK, 0660 ) ) > -1 ) {
        implement_simulated_keypresses = 1;
        printf("select_setup(): initializing simulation of keypresses from file '%s'\n", buffer);
     } else {
        fd = -1;
        printf("select_setup(): cannot simulate keypresses because cannot open '%s'\n", buffer);
     }


     sprintf(buffer, "%s/my-slow-down-factor.txt", cwd);
     printf("select_setup(): looking for '%s' to read slow-down-factor for emulation (100000 yields about 9 fps, 50000 about 14 fps)\n", buffer);
     fp = fopen(buffer, "r");
     if (fp) {
 	if(fscanf(fp, "%d", &slow_frame_rate_sleep_interval)) {
           implement_slow_frame_rate = 1;
 	  printf("Will slow frame rate by adding %d microseconds to each cycle\n", slow_frame_rate_sleep_interval);
  	} else {
 	  printf("Did not read a factor by which to slow the frame rate\n");
 	}
 	fclose(fp);
     } else {
         printf("Could not open file '%s' to read a factor by which to slow the frame rate\n", buffer);
     }
  }
  // 2020-11-02

  auto assign(uint inputID, bool value) -> void {
    auto& group = hid->buttons();
    if(group.input(inputID).value() == value) return;
    input.doChange(hid, HID::Keyboard::GroupID::Button, inputID, group.input(inputID).value(), value);
    group.input(inputID).setValue(value);
  }

  // 2020-11-02
  // This function is called regularly to poll the keyboard.
  //  XQueryKeymap gets the current state of all keys in a 32-byte buffer
  // The A key corresponds to inputID 35. So we can insert that value with 
  // assign(35, 1) when the flag is set, and then decrement the flag. The
  // next time we check the flag is when this function is polled again, which
  // hopefully will lead to better timing delays.
  // 2020-11-02
  auto poll(vector<shared_pointer<HID::Device>>& devices) -> void {
    char state[32];
    XQueryKeymap(display, state);

    uint inputID = 0;
    for(auto& key : keys) {
      bool value = state[key.keycode >> 3] & (1 << (key.keycode & 7));
      // 2020-11-17  set this flag when we see our first 'a' keypress
      // 2020-12-23  need to change from 'a' keypress to 1
      //  This edit is because no user will press 1 normally, so only the AI
      //  can trigger this slowdown code. This will only be necessary as long
      //  as the processing takes 3 seconds to do. 
      //2021-04-13 This is the code for the keyboard inputs, not for simulating keypresses
      if ((17== inputID) && (1 == value) && (1 == implement_slow_frame_rate)) {
       printf("Changing slow frame rate to 2 \n");
       implement_slow_frame_rate = 2;
       
       //file_operations opening file with time stuff
       epoch_time = time(NULL);
       ts = *localtime(&epoch_time);
       strftime(buff_time, sizeof buff_time, "%F_%T", &ts);
       sprintf(filepath_name, "/home/widman/Documents/School21Spring/ECEN_404/Implementation_new/Training_Folder/");
       sprintf(file_name, "%s/keylogger_%s", filepath_name, buff_time);
       file_keypresser = fopen(file_name, "a");	       
      }
      if ((18 == inputID) && (1 == value) && (2 == implement_slow_frame_rate))      {
	printf("Changing slow frame rate to 1 \n");
	implement_slow_frame_rate = 1;
	fclose(file_keypresser);
     }  
      if ((35 == inputID) && (2 == implement_slow_frame_rate) && (1 == value)){
	//epoch_time = time(NULL); 
   	   gettimeofday (&tvalBefore, NULL);

           printf("sec %ld, usec %ld\n", tvalBefore.tv_sec, tvalBefore.tv_usec);
           double our_usec = ((float)tvalBefore.tv_usec)/1000000.0;	
	// final_time_calc = (float)tvalBefore.tv_sec + ((float)tvalBefore.tv_usec)/1000000.0;
           final_time_calc = (double)(tvalBefore.tv_sec) + our_usec;
	//printf("usec time %.6lf, sec time %lf, final calc %.6lf \n", our_usec, (double)tvalBefore.tv_sec, final_time_calc);
	  //  printf("%d has been pressed at %.6lf", inputID, final_time_calc);
	  //fprintf(file_keypresser, "%.6lf %d\n",final_time_calc, inputID);
      }
      // 2020-11-17
      //2021-04-13 This requires changing the speed to read but it works
      //if (1 == value){
      //    printf("This is Key %d", inputID);
      //}


      //if ((84 == inputID) && (1 == implement_slow_frame_rate) && (1 == value)){
	//	printf("This is good");
	//}
      assign(inputID++, value);
    }

    // 2020-11-02
    // when it is time to simulate a keypress, we do this:
    select_poll();
    if ( simulate_keypress_flag ) {
      assign(35, 1);                // simulate keypress 'a'
      simulate_keypress_flag--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }
    // 2020-11-02

    if ( simulate_keypress_flag_one ) {
      assign(17, 1);                // simulate keypress '1'
      printf("Changing slow frame rate to 2 \n");
      implement_slow_frame_rate = 2;
      simulate_keypress_flag_one--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }
    
    if ( simulate_keypress_flag_two ) {
      assign(18, 1);                // simulate keypress '2'
      printf("Speeding slow frame rate to 1 \n");
      implement_slow_frame_rate = 1;
      simulate_keypress_flag_two--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }
    //2021-01-11

    //2021-04-13
    //Directional simulate keypresses

    if ( simulate_keypress_flag_three ) {
      assign(84, 1);                // simulate keypress 'UpArrow'
      simulate_keypress_flag_three--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }

    if ( simulate_keypress_flag_four ) {
      assign(85, 1);                // simulate keypress 'DownArrow'
      simulate_keypress_flag_four--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }
    if ( simulate_keypress_flag_five) {
      assign(86, 1);                // simulate keypress 'LeftArrow'
      simulate_keypress_flag_five--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }

    if ( simulate_keypress_flag_six ) {
      assign(87, 1);                // simulate keypress 'RightArrow'
      simulate_keypress_flag_six--;     // decrement the flag
      //printf("poll(): simulating keypress\n");
    }
    devices.append(hid);
  }

  auto initialize() -> bool {
    display = XOpenDisplay(0);

    keys.append({"Escape", XK_Escape});

    keys.append({"F1", XK_F1});
    keys.append({"F2", XK_F2});
    keys.append({"F3", XK_F3});
    keys.append({"F4", XK_F4});
    keys.append({"F5", XK_F5});
    keys.append({"F6", XK_F6});
    keys.append({"F7", XK_F7});
    keys.append({"F8", XK_F8});
    keys.append({"F9", XK_F9});
    keys.append({"F10", XK_F10});
    keys.append({"F11", XK_F11});
    keys.append({"F12", XK_F12});

    keys.append({"ScrollLock", XK_Scroll_Lock});
    keys.append({"Pause", XK_Pause});

    keys.append({"Tilde", XK_asciitilde});

    keys.append({"Num0", XK_0});
    keys.append({"Num1", XK_1});
    keys.append({"Num2", XK_2});
    keys.append({"Num3", XK_3});
    keys.append({"Num4", XK_4});
    keys.append({"Num5", XK_5});
    keys.append({"Num6", XK_6});
    keys.append({"Num7", XK_7});
    keys.append({"Num8", XK_8});
    keys.append({"Num9", XK_9});

    keys.append({"Dash", XK_minus});
    keys.append({"Equal", XK_equal});
    keys.append({"Backspace", XK_BackSpace});

    keys.append({"Insert", XK_Insert});
    keys.append({"Delete", XK_Delete});
    keys.append({"Home", XK_Home});
    keys.append({"End", XK_End});
    keys.append({"PageUp", XK_Prior});
    keys.append({"PageDown", XK_Next});

    keys.append({"A", XK_A});
    keys.append({"B", XK_B});
    keys.append({"C", XK_C});
    keys.append({"D", XK_D});
    keys.append({"E", XK_E});
    keys.append({"F", XK_F});
    keys.append({"G", XK_G});
    keys.append({"H", XK_H});
    keys.append({"I", XK_I});
    keys.append({"J", XK_J});
    keys.append({"K", XK_K});
    keys.append({"L", XK_L});
    keys.append({"M", XK_M});
    keys.append({"N", XK_N});
    keys.append({"O", XK_O});
    keys.append({"P", XK_P});
    keys.append({"Q", XK_Q});
    keys.append({"R", XK_R});
    keys.append({"S", XK_S});
    keys.append({"T", XK_T});
    keys.append({"U", XK_U});
    keys.append({"V", XK_V});
    keys.append({"W", XK_W});
    keys.append({"X", XK_X});
    keys.append({"Y", XK_Y});
    keys.append({"Z", XK_Z});

    keys.append({"LeftBracket", XK_bracketleft});
    keys.append({"RightBracket", XK_bracketright});
    keys.append({"Backslash", XK_backslash});
    keys.append({"Semicolon", XK_semicolon});
    keys.append({"Apostrophe", XK_apostrophe});
    keys.append({"Comma", XK_comma});
    keys.append({"Period", XK_period});
    keys.append({"Slash", XK_slash});

    keys.append({"Keypad0", XK_KP_0});
    keys.append({"Keypad1", XK_KP_1});
    keys.append({"Keypad2", XK_KP_2});
    keys.append({"Keypad3", XK_KP_3});
    keys.append({"Keypad4", XK_KP_4});
    keys.append({"Keypad5", XK_KP_5});
    keys.append({"Keypad6", XK_KP_6});
    keys.append({"Keypad7", XK_KP_7});
    keys.append({"Keypad8", XK_KP_8});
    keys.append({"Keypad9", XK_KP_9});

    keys.append({"Add", XK_KP_Add});
    keys.append({"Subtract", XK_KP_Subtract});
    keys.append({"Multiply", XK_KP_Multiply});
    keys.append({"Divide", XK_KP_Divide});
    keys.append({"Enter", XK_KP_Enter});

    keys.append({"Up", XK_Up});
    keys.append({"Down", XK_Down});
    keys.append({"Left", XK_Left});
    keys.append({"Right", XK_Right});

    keys.append({"Tab", XK_Tab});
    keys.append({"Return", XK_Return});
    keys.append({"Spacebar", XK_space});

    keys.append({"LeftControl", XK_Control_L});
    keys.append({"RightControl", XK_Control_R});
    keys.append({"LeftAlt", XK_Alt_L});
    keys.append({"RightAlt", XK_Alt_R});
    keys.append({"LeftShift", XK_Shift_L});
    keys.append({"RightShift", XK_Shift_R});
    keys.append({"LeftSuper", XK_Super_L});
    keys.append({"RightSuper", XK_Super_R});
    keys.append({"Menu", XK_Menu});

    hid->setVendorID(HID::Keyboard::GenericVendorID);
    hid->setProductID(HID::Keyboard::GenericProductID);
    hid->setPathID(0);

    for(auto& key : keys) {
      hid->buttons().append(key.name);
      key.keycode = XKeysymToKeycode(display, key.keysym);
    }

    // 2020-11-02
    select_setup();
    // 2020-11-02

    return true;
  }

  auto terminate() -> void {
    if(display) {
      XCloseDisplay(display);
      display = nullptr;
    }
  }
};
