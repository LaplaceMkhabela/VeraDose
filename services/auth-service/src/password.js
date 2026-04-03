/**
 * Evaluates password strength.
 * @param {string} password 
 * @returns {object} { score, label, feedback }
 */
function checkPasswordStrength(password) {
  let score = 0;
  let feedback = [];

  if (!password) return { score: 0, label: 'Very Weak', feedback: ['Password is required'] };

  // 1. Length Check
  if (password.length >= 8) {
    score++;
  } else {
    feedback.push('Password should be at least 8 characters long');
  }

  // 2. Contains Uppercase and Lowercase
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
    score++;
  } else {
    feedback.push('Use a mix of uppercase and lowercase letters');
  }

  // 3. Contains Numbers
  if (/\d/.test(password)) {
    score++;
  } else {
    feedback.push('Include at least one number');
  }

  // 4. Contains Special Characters
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    score++;
  } else {
    feedback.push('Include at least one special character (e.g., !@#$)');
  }

  // Bonus: Length boost for very long passwords
  if (password.length >= 16 && score < 4) {
    score++;
  }

  const labels = ['Very Weak', 'Weak', 'Fair', 'Strong', 'Very Strong'];
  
  return {
    score: score, // 0 to 4
    label: labels[score],
    feedback: feedback
  };
}

export default checkPasswordStrength;