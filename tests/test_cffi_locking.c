#include <sys/mman.h>

#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

#include "linked_list.h"
static LINKED_LIST_CONTAINER* queue;
static pthread_mutex_t lock;
static bool is_running;
static pthread_t thread = NULL;
static int seen = 0;
void *consume_records(void *threadid);
void add_record(char* record, unsigned long record_length);
void start(void);
int stop(void);



void *consume_records(void *threadid)
{
   char *record;
   // printf("Spoo%d\n", shared_record_size);
   long generation = 0;
   long last_seen_gen = -1;
   size_t record_size;
   while (is_running) {
      pthread_mutex_lock (&lock);
      record = (char *) linked_list_popleft(queue, &record_size);
      pthread_mutex_unlock (&lock);
      if (record == NULL) {
         continue;
      }
   	generation = strtol(record, (char**)NULL, 10);
   	if (generation == (last_seen_gen + 1)) {
	   	// printf("generation: %d, index: %d\n", generation, index);
	   	seen += 1;
	   	last_seen_gen = generation;
   	}
      free(record);
   }
   pthread_exit(NULL);
}


void add_record(char* record, unsigned long record_length){
   size_t record_size = sizeof(char)*record_length;
   void *value = malloc(record_size);
   memcpy(value, record, record_size);
   //acquire lock
   pthread_mutex_lock (&lock);

   //add to
   linked_list_append(
          queue,
          value, record_size, true,
          true);

   //release lock
   pthread_mutex_unlock (&lock);
}

void start(void) {
   seen = 0;
   queue = initialize_empty_linked_list(0);
   pthread_mutex_init(&lock, NULL);

	int rc = pthread_create(&thread, NULL, consume_records, 0);
    is_running = true;
      if (rc){
         printf("ERROR; return code from pthread_create() is %d\n", rc);
         is_running = false;
      }
}

int stop(void) {
   if (is_running) {
      pthread_mutex_destroy(&lock);
   }
   if (thread != NULL) {
      is_running = false;
      linked_list_free(queue);
   }
	return seen;
}
