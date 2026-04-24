import { useState } from 'react'
import AuthForm from '../components/AuthForm'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')

  const handleSuccess = () => {
    // 登录或注册成功后跳转到首页
    navigate('/')
  }

  const handleSwitchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">
            分享链接自动解析总结
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            {mode === 'login' ? '登录以使用高级功能' : '注册新账号'}
          </p>
        </div>
        
        <AuthForm
          mode={mode}
          onSuccess={handleSuccess}
          onSwitchMode={handleSwitchMode}
        />
      </div>
    </div>
  )
}