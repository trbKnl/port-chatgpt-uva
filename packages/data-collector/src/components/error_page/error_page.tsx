import {
  Title1,
  BodyLarge,
  Translator,
  ReactFactoryContext,
} from "@eyra/feldspar"
import TextBundle from "@eyra/feldspar"
import { PropsUIPageError } from "./types"

type Props = PropsUIPageError & ReactFactoryContext

export const ErrorPage = (props: Props): JSX.Element => {

  const { stacktrace } = props
  const { title, text } = prepareCopy(props)

  return (
    <div>
      <Title1 text={title} />
      <BodyLarge text={text} />
      <BodyLarge text={stacktrace} />
    </div>
  )
}

interface Copy {
  title: string
  text: string
}

function prepareCopy ({ locale }: Props): Copy {
  return {
    title: Translator.translate(title, locale),
    text: Translator.translate(text, locale)
  }
}

const title = new TextBundle()
  .add('en', 'Error, not your fault!')
  .add('nl', 'Foutje, niet jouw schuld!')
  .add('de', 'Fehler, nicht Ihre Schuld!')

const text = new TextBundle()
  .add('en', 'Consult the researcher, or close the page')
  .add('nl', 'Raadpleeg de onderzoeker of sluit de pagina')
  .add('de', 'Wenden Sie sich an den Forscher oder schließen Sie die Seite')
