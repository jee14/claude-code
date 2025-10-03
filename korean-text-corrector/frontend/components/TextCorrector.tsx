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
    if (isProcessing) return // 중복 요청 방지

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
      let searchStartIndex = 0
      const corrections: Correction[] = (data.corrections || []).map((c: any, idx: number) => {
        // Find position of original text starting from last found position
        const startIndex = data.original.indexOf(c.original, searchStartIndex)
        const endIndex = startIndex + c.original.length

        // Update search start index for next iteration
        if (startIndex >= 0) {
          searchStartIndex = endIndex
        }

        return {
          id: `${c.type}-${idx}`,
          type: c.type === 'spelling' ? 'spelling' as const : 'grammar' as const,
          original: c.original,
          corrected: c.corrected,
          explanation: c.explanation || `${c.original} → ${c.corrected}`,
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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <div className="max-w-5xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent mb-3">
            한국어 문장 다듬기
          </h1>
          <p className="text-slate-600 text-lg">텍스트를 입력하고 원하는 기능을 선택하세요.</p>
        </div>

        {/* Main Content */}
        <div className="space-y-6">
          {/* Input Section */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
            <textarea
              id="input-text"
              className="w-full h-48 p-4 border-0 focus:ring-0 focus:outline-none resize-none text-slate-900 placeholder:text-slate-400"
              placeholder="텍스트를 입력하세요."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              maxLength={1000}
            />
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <div className="text-sm text-slate-500">
                {inputText.length} / 1000자
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-3 gap-3">
            <button
              onClick={() => handleCorrection('proofreading')}
              disabled={!inputText.trim() || isProcessing}
              className="group relative px-6 py-4 bg-white border-2 border-slate-200 rounded-xl hover:border-blue-500 hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-slate-200 disabled:hover:bg-white transition-all duration-200"
            >
              <div className="text-left">
                <div className="font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">교정</div>
                <div className="text-xs text-slate-500 mt-1">맞춤법 • 띄어쓰기</div>
              </div>
            </button>

            <button
              onClick={() => handleCorrection('copyediting')}
              disabled={!inputText.trim() || isProcessing}
              className="group relative px-6 py-4 bg-white border-2 border-slate-200 rounded-xl hover:border-emerald-500 hover:bg-emerald-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-slate-200 disabled:hover:bg-white transition-all duration-200"
            >
              <div className="text-left">
                <div className="font-semibold text-slate-900 group-hover:text-emerald-600 transition-colors">교열</div>
                <div className="text-xs text-slate-500 mt-1">일관성 • 중복 제거</div>
              </div>
            </button>

            <button
              onClick={() => handleCorrection('rewriting')}
              disabled={!inputText.trim() || isProcessing}
              className="group relative px-6 py-4 bg-white border-2 border-slate-200 rounded-xl hover:border-violet-500 hover:bg-violet-50 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:border-slate-200 disabled:hover:bg-white transition-all duration-200"
            >
              <div className="text-left">
                <div className="font-semibold text-slate-900 group-hover:text-violet-600 transition-colors">윤문</div>
                <div className="text-xs text-slate-500 mt-1">문장 구조 개선</div>
              </div>
            </button>
          </div>

          {/* Mode Descriptions */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
            <div className="grid grid-cols-3 gap-4 text-xs">
              <div>
                <span className="font-semibold text-blue-600">교정:</span>
                <span className="text-slate-600 ml-1">맞춤법, 띄어쓰기, 문장부호 검사</span>
              </div>
              <div>
                <span className="font-semibold text-emerald-600">교열:</span>
                <span className="text-slate-600 ml-1">교정 + 문맥 일관성, 용어 통일, 중복 제거</span>
              </div>
              <div>
                <span className="font-semibold text-violet-600">윤문:</span>
                <span className="text-slate-600 ml-1">교정 + 교열 + 문장 구조 개선, 가독성 향상</span>
              </div>
            </div>
          </div>
          
          {isProcessing && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-12">
              <div className="flex flex-col items-center gap-4">
                <div className="w-8 h-8 border-3 border-slate-200 border-t-blue-500 rounded-full animate-spin"></div>
                <span className="text-slate-600 font-medium">처리 중...</span>
              </div>
            </div>
          )}
          
          {result && !isProcessing && (
            <div className="space-y-6 animate-in slide-in-from-bottom duration-300">
              {/* Result Header */}
              <div className="bg-gradient-to-r from-slate-50 to-slate-100 rounded-2xl p-6 border border-slate-200">
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  {result.mode === 'proofreading' && '교정'}
                  {result.mode === 'copyediting' && '교열'}
                  {result.mode === 'rewriting' && '윤문'}
                  {' '}결과
                </h3>
                <p className="text-sm text-slate-600">
                  {getModeDescription(result.mode)}
                </p>
              </div>

              {/* Corrected Text */}
              <div className="bg-white rounded-2xl shadow-sm border border-blue-200 p-6">
                <h4 className="text-sm font-semibold text-blue-700 mb-3">수정된 텍스트</h4>
                <div className="text-slate-900 leading-relaxed">
                  {result.correctedText}
                </div>
              </div>
              
              {result.corrections.length > 0 && (
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
                  <h4 className="text-sm font-semibold text-slate-700 mb-4">
                    수정 내역 <span className="text-slate-500">({result.corrections.length}개)</span>
                  </h4>
                  <div className="space-y-2">
                    {result.corrections.map((correction) => {
                      const typeConfig = {
                        spelling: { color: 'red', label: '맞춤법/띄어쓰기', bgColor: 'bg-red-50', borderColor: 'border-red-200', badgeColor: 'bg-red-100 text-red-700' },
                        grammar: { color: 'amber', label: '문법/일관성', bgColor: 'bg-amber-50', borderColor: 'border-amber-200', badgeColor: 'bg-amber-100 text-amber-700' },
                        style: { color: 'blue', label: '문체/구조', bgColor: 'bg-blue-50', borderColor: 'border-blue-200', badgeColor: 'bg-blue-100 text-blue-700' }
                      }[correction.type]

                      return (
                        <div
                          key={correction.id}
                          className={`flex items-start gap-3 p-4 ${typeConfig.bgColor} rounded-xl border ${typeConfig.borderColor} hover:shadow-sm transition-all`}
                        >
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${typeConfig.badgeColor}`}>
                                {typeConfig.label}
                              </span>
                            </div>
                            <div className="flex items-center gap-2 mb-2 flex-wrap">
                              <span className="text-slate-500 line-through text-sm">
                                {correction.original}
                              </span>
                              <span className="text-slate-400">→</span>
                              <span className="font-semibold text-emerald-700 text-sm">
                                {correction.corrected}
                              </span>
                            </div>
                            <p className="text-sm text-slate-700 leading-relaxed">
                              {correction.explanation}
                            </p>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}