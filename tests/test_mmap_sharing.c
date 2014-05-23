#include <sys/mman.h>

#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

static bool is_running;
static void* shared_mmap;
static int shared_mmap_limit;
static pthread_t thread = NULL;
static int shared_record_size;
static int seen = 0;

void *consume_mmap(void *threadid);

void *consume_mmap(void *threadid)
{
   char *record;
   int index = 0;
   // printf("Spoo%d\n", shared_record_size);
   int max_index = shared_mmap_limit / shared_record_size;
   long generation = 0;
   long last_seen_gen = -1;
   while (is_running) {
   	if (index == max_index) {
   		index = 0;
   	}
   	record = (char*) shared_mmap + (shared_record_size*index);
   	generation = strtol(record, (char**)NULL, 10);
   	index += 1;
   	if (generation == (last_seen_gen + 1)) {
	   	*record = '0';
	   	*(record + 1) = '0';
	   	*(record + 2) = '0';
	   	// printf("generation: %d, index: %d\n", generation, index);
	   	seen += 1;
	   	last_seen_gen = generation;
   	}
   }
   pthread_exit(NULL);
}

void link_mmap(void *mmap, int mmap_size, int record_size);
void start(void);
int stop(void);




void link_mmap(void *mmap, int mmap_size, int record_size) {
	shared_mmap = mmap;
	shared_mmap_limit = mmap_size;
	shared_record_size = record_size;
}

void start(void) {
	seen = 0;
	int rc = pthread_create(&thread, NULL, consume_mmap, 0);
    is_running = true;
      if (rc){
         printf("ERROR; return code from pthread_create() is %d\n", rc);
         is_running = false;
      }
}

int stop(void) {
	if (thread != NULL) {
		is_running = false;
	}
	return seen;
}
