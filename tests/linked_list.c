#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h> 
#include <string.h> 
#include <assert.h>
#include "linked_list.h"


LINKED_LIST_CONTAINER* initialize_empty_linked_list(int type_id) {
     LINKED_LIST_CONTAINER *new_list = (LINKED_LIST_CONTAINER *) malloc(sizeof(LINKED_LIST_CONTAINER));
     memset(new_list, 0, sizeof(LINKED_LIST_CONTAINER));
     new_list->head = NULL;
     new_list->tail = NULL;
     new_list->length = 0;
     new_list->type_id = type_id;
     assert(new_list->head == new_list->tail);
     return new_list;
}

void free_linked_list_element(NODE *node) {
     assert(node != NULL);
     if (node->free) {
          free(node->value);
     }
     free(node);
}

void linked_list_map(LINKED_LIST_CONTAINER *container, void(*callback) (NODE *node)) {
     unsigned int num_elements_left = container->length;
     NODE *node = container->head;
     NODE *next_node = NULL;
     if (NULL == node) {
          return;
     }
     while (num_elements_left > 0) {
          next_node = node->next;
          if (NULL == next_node) {
               break;
          }
          callback(node);

          node = next_node;
          num_elements_left--;
     }
     return;
}

void* linked_list_popleft(LINKED_LIST_CONTAINER* container, size_t *node_size) {
     unsigned int num_elements_left = container->length;
     if (num_elements_left == 0) {
          return NULL;
     }
     NODE *node = container->head;
     NODE *next_node = NULL;
     if (node == NULL) {
          return NULL;
     }
     next_node = node->next;
     if (next_node != NULL) {
          next_node->prev = NULL;
     }

     container->head = next_node;
     if (container->tail == node) {
          container->tail = next_node;
     }
     container->length = num_elements_left - 1;
     *node_size = node->value_size;
     return node->value;
}


/*
* Add to the buffer with a two pass scan provided by callback, which returns true or false
*/


LINKED_LIST_CONTAINER* linked_list_select(LINKED_LIST_CONTAINER *container, bool(*callback)(NODE *)) {
     LINKED_LIST_CONTAINER* retval = (LINKED_LIST_CONTAINER *) malloc(sizeof(LINKED_LIST_CONTAINER));
     memset(retval, 0, sizeof(LINKED_LIST_CONTAINER));
     retval->length = 0;
     retval->head = NULL;
     retval->tail = NULL;

     NODE *node = container->head;
     NODE *new_node = NULL;

     while (NULL != node) {
          if (callback(node)) {
               new_node = (NODE *)malloc(sizeof(NODE));
               memcpy(new_node, node, sizeof(NODE));
               new_node->value = (void *) malloc(node->value_size);
               memcpy(new_node->value, node->value, node->value_size);

               if (NULL == retval->head) {
                    new_node->prev = NULL;
                    new_node->next = NULL;
                    retval->head = new_node;
                    retval->tail = new_node;
               } else {
                    new_node->prev = retval->tail;
                    new_node->next = NULL;
                    retval->tail->next = new_node;
                    retval->tail = new_node;
               }
               retval->length++;
          }
          node = node->next;
     }
     return retval;
}


void linked_list_free(LINKED_LIST_CONTAINER *container) {
     linked_list_map(container, &free_linked_list_element);
     free(container);
}



void linked_list_append(
          LINKED_LIST_CONTAINER *container,
          void *value, size_t value_size, bool free_value,
          bool direction_tail) {
     DEBUG_PRINTF(("(linked_list_append) Num elements %d\n", container->length));

     NODE *node = (NODE *)malloc(sizeof(NODE));
     memset(node, 0, sizeof(NODE));
     node->value = value;
     node->value_size = value_size;
     node->free = free_value;
     node->next = NULL;
     node->prev = NULL;

     if (NULL == container->head) {
          DEBUG_PRINTF(("(linked_list_append) Head assigned.\n"));
          container->head = node;
     }
     if (NULL == container->tail) {
          DEBUG_PRINTF(("(linked_list_append) Tail assigned. %p\n", node));
          container->tail = node;
     }

     if (container->length) {
          if (direction_tail) {
               /* ensure the new tail considers the previous tail it's prev
               and the next element NULL
               */
               node->prev = container->tail;
               node->next = NULL;
               /* Ensure the current tail (before we change it) considers the new node it's successor */
               DEBUG_PRINTF(("(linked_list_append) Current Tail Memory Address: %p\n", container->tail));
               container->tail->next = node;

               /* Ensure the tail is set to the new node */
               container->tail = node;
          } else {
               /* ensure the new head considers the previous head it's prev
               and the next element NULL
               */
               node->prev = NULL;
               node->next = container->head;
               /* Ensure the current head (before we change it) considers the new node it's successor */
               container->head->prev = node;

               /* Ensure the head is set to the new node */
               container->head = node;
          }
     }
     container->length += 1;
     return;
}

ARRAY* linked_list_to_array(LINKED_LIST_CONTAINER *container) {
     unsigned int num_elements_left = container->length;
     unsigned int i = 0;
     ARRAY *result = (ARRAY *) malloc(sizeof(ARRAY));
     memset(result, 0, sizeof(ARRAY));
     if (container->length == 0) {
          return result;
     }

     assert(container->length <= MAXIMUM_CONTAINER_LENGTH);
     NODE *node = container->head;
     NODE *new_node;
     NODE *nodes = (NODE *) malloc(sizeof(NODE) * (container->length));
     result->nodes = nodes;
     result->length = container->length;

     while (i < num_elements_left) {
          memcpy(&(nodes[i]), node, sizeof(NODE));
          new_node = &nodes[i];
          new_node->free = node->free;
          new_node->value = (void *) malloc(node->value_size);
          memcpy(new_node->value, node->value, node->value_size);
          node = node->next;
          i++;
     }
     return result;
}


