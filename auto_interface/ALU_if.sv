

interface ALU_if();

//input/output signals
    logic [31:0] a_operand=32'h0;
    logic [31:0] b_operand;
    logic [3:0] Operation;
    logic [31:0] ALU_Output;
    logic  Exception;
    logic  Overflow;
    logic  Underflow;
    logic  clk;


    modport DUT (
    input a_operand=32'h0, b_operand, Operation, clk,
    output ALU_Output, Exception, Overflow, Underflow
    );//design modport
    
endinterface //ALU design interface
