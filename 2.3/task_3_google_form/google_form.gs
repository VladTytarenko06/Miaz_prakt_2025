/**
 * Додатково: створити форму з власним переліком відділів.
 * Виклик: createFormWithDepartments(['Sales','Marketing','Finance']);
 */
function createFormWithDepartments(departments) {
  if (!departments || !departments.length) {
    departments = ['Відділ продажів', 'Відділ маркетингу', 'Бухгалтерія', 'HR', 'ІТ-відділ'];
  }
  var form = FormApp.create('Збір даних співробітників')
    .setDescription('Автоматично створена форма з кастомним переліком відділів.')
    .setIsQuiz(false)
    .setCollectEmail(false);

  form.addTextItem().setTitle('Ім’я та прізвище').setRequired(true);
  form.addDateItem().setTitle('Дата').setRequired(true);
  form.addListItem().setTitle('Відділ').setChoiceValues(departments).setRequired(true);

  Logger.log('Форма створена (редагування): ' + form.getEditUrl());
  Logger.log('Посилання для заповнення: ' + form.getPublishedUrl());
}
