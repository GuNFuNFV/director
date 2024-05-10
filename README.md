# how to add a network function
## in the director
  ### orchestration/composed_nf_definition
     1. add a nf type
        nf_type
           category
              system
              stateless nf
              stateful nf
              stateful match
           parameters
           flow_state_variables
           transition
     2. add nfd in composed_nf_definition_file
     3. add experiment in exp_name_to_conjecture_data_dic_list
     4. run the python script of configuration generation

## In the runtime
  ### create a nf 
    1. c file 
       containers the initialize the control state for the network function
       if it a classifier, then it contains classifier init
    2. header file
       define the control state
    3. add related actions to actor table in worker_amac.c this is automatically handled by a python script