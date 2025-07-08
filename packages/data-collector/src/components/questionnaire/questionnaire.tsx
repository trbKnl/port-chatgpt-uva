import React from 'react'
import {
  Translator,
  ReactFactoryContext,
  PrimaryButton,
} from "@eyra/feldspar"
import TextBundle from "@eyra/feldspar"
import { 
    PropsUIPromptQuestionnaire,
    isPropsUIQuestionMultipleChoice,
    isPropsUIQuestionMultipleChoiceCheckbox,
    isPropsUIQuestionOpen,
} from "./types"

import { MultipleChoiceQuestion } from './multiple_choice_question'
import { MultipleChoiceQuestionCheckbox } from './multiple_choice_question_checkbox'
import { OpenQuestion } from './open_question'

type Props = PropsUIPromptQuestionnaire & ReactFactoryContext

export const Questionnaire = (props: Props): JSX.Element => {
  const { questions, description, questionToChatgpt, answerFromChatgpt, resolve, locale } = props
  const [answers, setAnswers] = React.useState<{}>({});
  const copy = prepareCopy(locale)

    
  React.useEffect(() => {
    // check if running in an iframe
    if (window.frameElement) {
      window.parent.scrollTo(0,0)
    } else {
      window.scrollTo(0,0)
    }
  }, [])

  function handleDonate (): void {
    const toStore = {
     ...answers, 
     "questionToChatgpt": questionToChatgpt, 
     "answerFromChatgpt": answerFromChatgpt, 
    }
    const value = JSON.stringify(toStore)
    resolve?.({ __type__: 'PayloadJSON', value })
  }

  const renderQuestion = (item: any) => {
    if (isPropsUIQuestionMultipleChoice(item)) {
      return (
        <div key={item.id}>
          <MultipleChoiceQuestion {...item} locale={locale} parentSetter={setAnswers} />
        </div>
      )
    }
    if (isPropsUIQuestionMultipleChoiceCheckbox(item)) {
      return (
        <div key={item.id}>
          <MultipleChoiceQuestionCheckbox {...item} locale={locale} parentSetter={setAnswers} />
        </div>
      )
    }
    if (isPropsUIQuestionOpen(item)) {
      return (
        <div key={item.id}>
          <OpenQuestion {...item} locale={locale} parentSetter={setAnswers} />
        </div>
      )
    }
  }

  const renderQuestions = () => {
   return questions.map((item) => renderQuestion(item))
  }

  return (
    <div>
      <div className='flex-wrap text-bodylarge font-body text-grey1 text-left'>
        {copy.description}
      </div>

      <div className='bg-primarylight rounded-lg shadow-md p-6 mt-4 mb-4'>
        <h3 className='text-lg font-semibold mb-2'>
            {copy.questionChatgptLabel}
        </h3>
        <div className='text-base'>
            {questionToChatgpt.split('\n').map((line: string, index: number) => (
            <p className="mt-2" key={index}>
                {line}
            </p>
            ))}
        </div>
      </div>

      <div className='bg-successlight rounded-lg shadow-md p-6 mt-4 mb-4'>
        <h3 className='text-lg font-semibold mb-2'>
            {copy.answerChatgptLabel}
        </h3>
        <div className='text-base'>
            {answerFromChatgpt.split('\n').map((line: string, index: number) => (
            <p className="mt-2" key={index}>
                {line}
            </p>
            ))}
        </div>
      </div>

      <div>
        {renderQuestions()}
      </div>
      <div className='flex flex-row gap-4 mt-4 mb-4'>
        <PrimaryButton label={copy.continueLabel} onClick={handleDonate} color='bg-success text-white' />
      </div>
    </div>
  );

        
  function prepareCopy (locale: string): Copy {
    return {
      description: Translator.translate(description, locale),
      continueLabel: Translator.translate(continueLabel, locale),
      questionChatgptLabel: Translator.translate(questionChatgptLabel, locale),
      answerChatgptLabel: Translator.translate(answerChatgptLabel, locale),
    }
  }
};


interface Copy {
  description: string
  continueLabel: string
  questionChatgptLabel: string
  answerChatgptLabel: string
}


const continueLabel = new TextBundle()
  .add('en', 'Continue')
  .add('nl', 'Verder')


const questionChatgptLabel = new TextBundle()
  .add('en', 'Your question to ChatGPT')
  .add('nl', 'Jouw vraag aan ChatGPT')


const answerChatgptLabel = new TextBundle()
  .add('en', 'The answer from ChatGPT')
  .add('nl', 'Het antwoord van ChatGPT')
