#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#ifdef DEBUG
# define DEBUG_PRINTF(x) printf x
#else
# define DEBUG_PRINTF(x) do {} while (0)
#endif

/* This would allow for 4 gigabytes of NODEs */
#define MAXIMUM_CONTAINER_LENGTH 130150524

struct node_t;

typedef struct node_t {
     void *value; //4 or 8
     struct node_t *next; //4 or 8
     struct node_t *prev; //4 or 8
     bool free; //1
     size_t value_size; //this will allow a memcpy to duplicate on the heap
} NODE;


typedef struct ARRAY {
     unsigned long length;
     NODE* nodes;
} ARRAY;



typedef struct LINKED_LIST_CONTAINER {
     unsigned int length; //4
     int type_id; //4

     NODE *head; //4 or 8
     /*
     I have no fucking idea why this requires it to be pointer size *2 to make
     it work on 64bit and 32bit.
     */
     // char padding[sizeof (char*)*2];
     NODE *tail; //4 or 8
} LINKED_LIST_CONTAINER;

LINKED_LIST_CONTAINER* initialize_empty_linked_list(int type_id);
void free_linked_list_element(NODE *node);
void linked_list_map(LINKED_LIST_CONTAINER *container, void(*callback) (NODE *node));
void linked_list_free(LINKED_LIST_CONTAINER *container);
void linked_list_append(
          LINKED_LIST_CONTAINER *container,
          void *value, size_t value_size, bool free_value,
          bool direction_tail);

ARRAY* linked_list_to_array(LINKED_LIST_CONTAINER *container);

typedef struct NODE_SELECT {
     NODE** results;
     unsigned int num_results;
} NODE_SELECT;
void* linked_list_popleft(LINKED_LIST_CONTAINER* container, size_t *node_size);

// NODE_SELECT* linked_list_select(LINKED_LIST_CONTAINER *container, bool(*callback)(NODE *));
LINKED_LIST_CONTAINER* linked_list_select(LINKED_LIST_CONTAINER *container, bool(*callback)(NODE *));
