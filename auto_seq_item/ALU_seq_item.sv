
import uvm_pkg::*;
`include "uvm_macros.svh"

// Define operation codes for clarity in constraints
typedef enum logic [3:0] {
  MULTIPLICATION = 4'd1,
  DIVISION       = 4'd2,
  SUBTRACTION    = 4'd3,
  OR_OP          = 4'd4,
  AND_OP         = 4'd5,
  XOR_OP         = 4'd6,
  LEFT_SHIFT     = 4'd7,
  RIGHT_SHIFT    = 4'd8,
  FP_TO_INT      = 4'd9,
  ADDITION       = 4'd10,
  COMPLEMENT     = 4'd11
} operation_t;

/**
 * @class ALU_seq_item
 * @brief Sequence item for the ALU module.
 *
 * This class defines the transaction item sent from the sequencer to the driver.
 * It contains all the input signals that need to be randomized and driven to the DUT,
 * as well as the output signals that will be captured by the monitor.
 */
class ALU_seq_item extends uvm_sequence_item;

  //----------------------------------------------------------------------------
  // UVM Factory Registration
  //----------------------------------------------------------------------------
  `uvm_object_utils(ALU_seq_item)

  //----------------------------------------------------------------------------
  // Member variables for DUT I/O
  //----------------------------------------------------------------------------
  // Inputs (randomized)
  rand logic [31:0] a_operand;
  rand logic [31:0] b_operand;
  rand operation_t  Operation;

  // Clock signal (not randomized)
  bit clk;

  // Outputs (not randomized)
  logic [31:0] ALU_Output;
  logic        Exception;
  logic        Overflow;
  logic        Underflow;

  //----------------------------------------------------------------------------
  // Helper variables for operand constraints
  //----------------------------------------------------------------------------
  // These variables break down the floating-point operands into their
  // constituent parts (sign, exponent, mantissa) to allow for more
  // targeted and readable constraints.
  rand logic        a_sign;
  rand logic [7:0]  a_exponent;
  rand logic [22:0] a_mantissa;

  rand logic        b_sign;
  rand logic [7:0]  b_exponent;
  rand logic [22:0] b_mantissa;

  //----------------------------------------------------------------------------
  // Constraints
  //----------------------------------------------------------------------------

  // Constraint to ensure the generated operation is one of the validly defined operations.
  constraint c_valid_operation {
    Operation inside {
      MULTIPLICATION, DIVISION, SUBTRACTION, OR_OP, AND_OP, XOR_OP,
      LEFT_SHIFT, RIGHT_SHIFT, FP_TO_INT, ADDITION, COMPLEMENT
    };
  }

  // Constraint to assemble the floating-point operands from their constituent parts.
  // This allows constraining sign, exponent, and mantissa fields individually.
  constraint c_build_operands {
    // This constraint is bidirectional. It ensures that if a_operand is randomized,
    // the helper variables are updated, and if the helper variables are randomized,
    // a_operand is correctly formed.
    a_operand == {a_sign, a_exponent, a_mantissa};
    b_operand == {b_sign, b_exponent, b_mantissa};
  }

  // Constraint to generate a distribution of different floating-point number types
  // based on the exponent value, covering normal, subnormal, zero, infinity, and NaN cases.
  constraint c_fp_type_distribution {
    // This distribution is weighted to generate more normal numbers, but still
    // provides coverage for special cases.
    // 70% chance for Normal numbers (exponent 1-254)
    // 15% chance for Zero/Subnormal numbers (exponent 0)
    // 15% chance for Infinity/NaN (exponent 255)
    a_exponent dist { [1:254] := 70, 8'h00 := 15, 8'hFF := 15 };
    b_exponent dist { [1:254] := 70, 8'h00 := 15, 8'hFF := 15 };
  }

  // Constraint to differentiate between Zero and Subnormal numbers when exponent is 0.
  constraint c_zero_subnormal_mantissa {
    // If exponent is 0, 50% chance the mantissa is 0 (Zero), 50% chance it's non-zero (Subnormal).
    (a_exponent == 8'h00) -> a_mantissa dist { 0 := 1, [1:'1] := 1 };
    (b_exponent == 8'h00) -> b_mantissa dist { 0 := 1, [1:'1] := 1 };
  }

  // Constraint to differentiate between Infinity and NaN when exponent is 255.
  constraint c_inf_nan_mantissa {
    // If exponent is 255, 50% chance the mantissa is 0 (Infinity), 50% chance it's non-zero (NaN).
    (a_exponent == 8'hFF) -> a_mantissa dist { 0 := 1, [1:'1] := 1 };
    (b_exponent == 8'hFF) -> b_mantissa dist { 0 := 1, [1:'1] := 1 };
  }

  // Constraint specific to shift operations.
  // The shift amount is determined by b_operand. For a 32-bit shift, only the
  // lower 5 bits are typically used. This constraint ensures the upper bits are zero
  // to avoid ambiguity and test realistic shift amounts (0-31).
  constraint c_shift_amount {
    (Operation == LEFT_SHIFT || Operation == RIGHT_SHIFT) -> b_operand[31:5] == 0;
  }

  //----------------------------------------------------------------------------
  // Constructor
  //----------------------------------------------------------------------------
  function new(string name = "ALU_seq_item");
    super.new(name);
  endfunction : new

endclass : ALU_seq_item
