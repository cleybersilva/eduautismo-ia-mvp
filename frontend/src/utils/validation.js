import { z } from 'zod';

/**
 * Schema de validação para login
 */
export const loginSchema = z.object({
  email: z.string()
    .email('Por favor, insira um email válido')
    .min(5, 'Email muito curto')
    .max(255, 'Email muito longo'),
  password: z.string()
    .min(6, 'A senha deve ter no mínimo 6 caracteres')
    .max(128, 'Senha muito longa')
});

/**
 * Schema de validação para registro
 */
export const registerSchema = z.object({
  name: z.string()
    .min(3, 'Nome deve ter no mínimo 3 caracteres')
    .max(255, 'Nome muito longo'),
  email: z.string()
    .email('Por favor, insira um email válido')
    .min(5, 'Email muito curto')
    .max(255, 'Email muito longo'),
  password: z.string()
    .min(8, 'A senha deve ter no mínimo 8 caracteres')
    .regex(/[A-Z]/, 'A senha deve conter pelo menos uma letra maiúscula')
    .regex(/[a-z]/, 'A senha deve conter pelo menos uma letra minúscula')
    .regex(/[0-9]/, 'A senha deve conter pelo menos um número')
    .regex(/[^A-Za-z0-9]/, 'A senha deve conter pelo menos um caractere especial'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "As senhas não coincidem",
  path: ["confirmPassword"],
});

/**
 * Valida dados de formulário
 * @param {object} schema - Schema Zod
 * @param {object} data - Dados para validar
 * @returns {object} - { success: boolean, errors: object | null, data: object | null }
 */
export const validateForm = (schema, data) => {
  try {
    const validated = schema.parse(data);
    return { success: true, errors: null, data: validated };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const formattedErrors = error.flatten().fieldErrors;
      return { success: false, errors: formattedErrors, data: null };
    }
    return { success: false, errors: { _form: ['Erro de validação desconhecido'] }, data: null };
  }
};
