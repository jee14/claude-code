'use client'

import { useState } from 'react'

type CorrectionType = 'proofreading' | 'copyediting' | 'rewriting'
type ErrorType = 'spelling' | 'grammar' | 'style'

interface Correction {
  id: string
  type: ErrorType
  original: string
  corrected: string
  explanation: string
  startIndex: number
  endIndex: number
}

interface CorrectionResult {
  originalText: string
  correctedText: string
  corrections: Correction[]
  mode: CorrectionType
}

const mockCorrections: Record<CorrectionType, (text: string) => Correction[]> = {
  proofreading: (text) => {
    const corrections: Correction[] = []
    
    // 맞춤법 검사 예시
    if (text.includes('됬')) {
      const index = text.indexOf('됬')
      corrections.push({
        id: '1',
        type: 'spelling',
        original: '됬',
        corrected: '됐',
        explanation: '"됬"는 잘못된 표기입니다. "되었"의 준말은 "됐"입니다.',
        startIndex: index,
        endIndex: index + 1
      })
    }
    
    // 띄어쓰기 검사 예시
    const noSpacePattern = /([가-힣]+)(할수있)/g
    let match
    while ((match = noSpacePattern.exec(text)) !== null) {
      corrections.push({
        id: `space-${match.index}`,
        type: 'spelling',
        original: match[2],
        corrected: '할 수 있',
        explanation: '"할 수 있다"는 띄어쓰기가 필요한 구조입니다.',
        startIndex: match.index + match[1].length,
        endIndex: match.index + match[0].length
      })
    }
    
    return corrections
  },
  
  copyediting: (text) => {
    const corrections: Correction[] = []
    
    // 문맥 일관성 검사 예시
    if (text.includes('나는') && text.includes('저는')) {
      corrections.push({
        id: 'consistency-1',
        type: 'grammar',
        original: '나는',
        corrected: '저는',
        explanation: '문서 전체에서 높임 표현을 일관되게 사용하는 것이 좋습니다.',
        startIndex: text.indexOf('나는'),
        endIndex: text.indexOf('나는') + 2
      })
    }
    
    // 중복 표현 제거
    if (text.includes('역시 또한')) {
      const index = text.indexOf('역시 또한')
      corrections.push({
        id: 'redundancy-1',
        type: 'grammar',
        original: '역시 또한',
        corrected: '또한',
        explanation: '"역시"와 "또한"은 의미가 중복되므로 하나만 사용하는 것이 좋습니다.',
        startIndex: index,
        endIndex: index + 5
      })
    }
    
    return corrections
  },
  
  rewriting: (text) => {
    const corrections: Correction[] = []
    
    // 문장 구조 개선 예시
    const longSentencePattern = /[^.!?]{100,}/g
    let match
    while ((match = longSentencePattern.exec(text)) !== null) {
      corrections.push({
        id: `long-${match.index}`,
        type: 'style',
        original: match[0].substring(0, 50) + '...',
        corrected: '(문장을 2-3개로 나누기)',
        explanation: '문장이 너무 길어 가독성이 떨어집니다. 적절히 나누어 주세요.',
        startIndex: match.index,
        endIndex: match.index + 50
      })
    }
    
    // 수동태를 능동태로
    if (text.includes('되어진다')) {
      const index = text.indexOf('되어진다')
      corrections.push({
        id: 'passive-1',
        type: 'style',
        original: '되어진다',
        corrected: '된다',
        explanation: '불필요한 피동 표현입니다. 간결하게 "된다"로 바꾸는 것이 좋습니다.',
        startIndex: index,
        endIndex: index + 5
      })
    }
    
    return corrections
  }
}

export default function TextCorrector() {
  const [inputText, setInputText] = useState('')
  const [result, setResult] = useState<CorrectionResult | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)

  const handleCorrection = async (mode: CorrectionType) => {
    if (!inputText.trim()) return
    if (inputText.length > 1000) {
      alert('텍스트는 최대 1000자까지 입력 가능합니다.')
      return
    }

    setIsProcessing(true)

    try {
      const response = await fetch('http://localhost:8000/correct/detailed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText,
          mode: mode
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`)
      }

      const data = await response.json()

      // Debug: log the response
      console.log('API Response:', data)
      console.log('Original text:', data.original)
      console.log('Corrected text:', data.corrected)
      console.log('Corrections:', data.corrections)

      // Transform backend response to frontend format
      const corrections: Correction[] = (data.corrections || []).map((c: any, idx: number) => {
        // Find position of original text
        const startIndex = data.original.indexOf(c.original)
        const endIndex = startIndex + c.original.length

        return {
          id: `${c.type}-${idx}`,
          type: c.type === 'spelling' ? 'spelling' as const : 'grammar' as const,
          original: c.original,
          corrected: c.corrected,
          explanation: `${c.original} → ${c.corrected}`,
          startIndex: startIndex >= 0 ? startIndex : 0,
          endIndex: endIndex >= 0 ? endIndex : 0
        }
      })

      setResult({
        originalText: data.original,
        correctedText: data.corrected,
        corrections,
        mode
      })
    } catch (error) {
      console.error('Correction error:', error)
      alert('교정 중 오류가 발생했습니다. 다시 시도해주세요.')
    } finally {
      setIsProcessing(false)
    }
  }

  const getModeDescription = (mode: CorrectionType) => {
    switch (mode) {
      case 'proofreading':
        return '맞춤법, 띄어쓰기, 문장부호 등 기본적인 오류를 검사합니다.'
      case 'copyediting':
        return '문맥의 일관성, 용어 통일, 중복 표현 등을 검토합니다.'
      case 'rewriting':
        return '문장 구조를 개선하고 가독성을 높입니다.'
    }
  }

  const renderHighlightedText = (text: string, corrections: Correction[]) => {
    if (!corrections.length) return text
    
    let lastIndex = 0
    const elements: JSX.Element[] = []
    
    corrections.forEach((correction, idx) => {
      if (correction.startIndex > lastIndex) {
        elements.push(
          <span key={`text-${idx}`}>
            {text.slice(lastIndex, correction.startIndex)}
          </span>
        )
      }
      
      elements.push(
        <span
          key={`correction-${idx}`}
          className={`correction-highlight ${correction.type} cursor-pointer relative group`}
        >
          {text.slice(correction.startIndex, correction.endIndex)}
          <span className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-64 p-2 bg-gray-900 text-white text-sm rounded shadow-lg z-10">
            {correction.explanation}
          </span>
        </span>
      )
      
      lastIndex = correction.endIndex
    })
    
    if (lastIndex < text.length) {
      elements.push(<span key="end">{text.slice(lastIndex)}</span>)
    }
    
    return <>{elements}</>
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-2">한국어 문장 다듬기</h1>
        <p className="text-gray-600 mb-8">텍스트를 입력하고 원하는 기능을 선택하세요.</p>
        
        <div className="space-y-6">
          <div>
            <label htmlFor="input-text" className="block text-sm font-medium text-gray-700 mb-2">
              텍스트 입력
            </label>
            <textarea
              id="input-text"
              className="w-full h-40 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="텍스트를 입력하세요... (최대 1000자)"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              maxLength={1000}
            />
            <div className="text-right text-sm text-gray-500 mt-1">
              {inputText.length} / 1000자
            </div>
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={() => handleCorrection('proofreading')}
              disabled={!inputText.trim() || isProcessing}
              className="flex-1 py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <span className="font-medium">교정</span>
              <span className="block text-xs mt-1 opacity-90">맞춤법 • 띄어쓰기</span>
            </button>

            <button
              onClick={() => handleCorrection('copyediting')}
              disabled={!inputText.trim() || isProcessing}
              className="flex-1 py-3 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <span className="font-medium">교열</span>
              <span className="block text-xs mt-1 opacity-90">일관성 • 중복 제거</span>
            </button>

            <button
              onClick={() => handleCorrection('rewriting')}
              disabled={!inputText.trim() || isProcessing}
              className="flex-1 py-3 px-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <span className="font-medium">윤문</span>
              <span className="block text-xs mt-1 opacity-90">문장 구조 개선</span>
            </button>
          </div>
          
          {isProcessing && (
            <div className="text-center py-8">
              <div className="inline-flex items-center gap-2">
                <div className="w-5 h-5 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin"></div>
                <span className="text-gray-600">처리 중...</span>
              </div>
            </div>
          )}
          
          {result && !isProcessing && (
            <div className="space-y-6 animate-in slide-in-from-bottom duration-300">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-medium text-gray-700 mb-2">
                  {result.mode === 'proofreading' && '교정'}
                  {result.mode === 'copyediting' && '교열'}
                  {result.mode === 'rewriting' && '윤문'}
                  {' '}결과
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  {getModeDescription(result.mode)}
                </p>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">원본 텍스트</h4>
                <div className="p-4 bg-gray-50 rounded-lg leading-relaxed">
                  {renderHighlightedText(result.originalText, result.corrections)}
                </div>
              </div>
              
              <div>
                <h4 className="font-medium text-gray-700 mb-2">수정된 텍스트</h4>
                <div className="p-4 bg-blue-50 rounded-lg leading-relaxed">
                  {result.correctedText}
                </div>
              </div>
              
              {result.corrections.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-3">
                    수정 내역 ({result.corrections.length}개)
                  </h4>
                  <div className="space-y-3">
                    {result.corrections.map((correction) => (
                      <div
                        key={correction.id}
                        className="flex gap-3 p-4 bg-white border border-gray-200 rounded-lg"
                      >
                        <div className={`w-1 flex-shrink-0 rounded ${
                          correction.type === 'spelling' ? 'bg-red-500' :
                          correction.type === 'grammar' ? 'bg-amber-500' :
                          'bg-blue-500'
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-gray-500 line-through text-sm">
                              {correction.original}
                            </span>
                            <span className="text-gray-400">→</span>
                            <span className="font-medium text-green-600">
                              {correction.corrected}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">
                            {correction.explanation}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex items-center gap-6 text-sm text-gray-500">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span>맞춤법</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
                  <span>문법</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span>문체</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}