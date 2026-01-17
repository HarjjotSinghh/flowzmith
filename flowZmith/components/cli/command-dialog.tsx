"use client"

import * as React from "react"
import { Loader2, CheckCircle2, XCircle, ArrowRight, ArrowLeft, Terminal } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { CLICommand, CommandField } from "@/lib/cli-commands"

interface CommandDialogProps {
  command: CLICommand | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onExecute: (command: CLICommand, data: any) => Promise<any>
}

export function CommandDialog({ command, open, onOpenChange, onExecute }: CommandDialogProps) {
  const [currentStep, setCurrentStep] = React.useState(0)
  const [isExecuting, setIsExecuting] = React.useState(false)
  const [executionResult, setExecutionResult] = React.useState<any>(null)
  const [formData, setFormData] = React.useState<Record<string, any>>({})

  const useSheetLayout = command?.steps && command.steps.length > 1

  React.useEffect(() => {
    if (!open) {
      setCurrentStep(0)
      setIsExecuting(false)
      setExecutionResult(null)
      setFormData({})
    }
  }, [open])

  if (!command) return null

  const handleFieldChange = (fieldName: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }))
  }

  const handleNext = () => {
    if (command.steps && currentStep < command.steps.length - 1) {
      setCurrentStep(prev => prev + 1)
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      const result = await onExecute(command, formData)
      setExecutionResult(result)
    } catch (error: any) {
      setExecutionResult({ status: "failed", error: error.message })
    } finally {
      setIsExecuting(false)
    }
  }

  const renderField = (field: CommandField) => {
    const value = formData[field.name] ?? field.defaultValue ?? ""

    switch (field.type) {
      case "textarea":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-[10px] font-black uppercase tracking-widest">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Textarea
              id={field.name}
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              rows={4}
              className="rounded-none border-2 border-foreground bg-background font-bold text-xs uppercase"
            />
            {field.helpText && (
              <p className="text-[10px] font-bold text-foreground/50 uppercase italic">{`// ${field.helpText}`}</p>
            )}
          </div>
        )

      case "select":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-[10px] font-black uppercase tracking-widest">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Select
              value={value}
              onValueChange={(val) => handleFieldChange(field.name, val)}
            >
              <SelectTrigger className="rounded-none border-2 border-foreground bg-background font-bold text-xs uppercase h-12">
                <SelectValue placeholder={field.placeholder} />
              </SelectTrigger>
              <SelectContent className="rounded-none border-2 border-foreground bg-background">
                {field.options?.map((option) => (
                  <SelectItem key={option.value} value={option.value} className="font-bold text-xs uppercase">
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {field.helpText && (
              <p className="text-[10px] font-bold text-foreground/50 uppercase italic">{`// ${field.helpText}`}</p>
            )}
          </div>
        )

      case "checkbox":
        return (
          <div key={field.name} className="flex items-center space-x-3 p-3 border-2 border-foreground bg-muted/5 group hover:bg-accent transition-colors">
            <Checkbox
              id={field.name}
              checked={value}
              onCheckedChange={(checked) => handleFieldChange(field.name, checked)}
              className="border-2 border-foreground rounded-none data-[state=checked]:bg-foreground data-[state=checked]:text-background"
            />
            <Label htmlFor={field.name} className="cursor-pointer text-[10px] font-black uppercase tracking-widest group-hover:text-black">
              {field.label}
            </Label>
          </div>
        )

      case "number":
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-[10px] font-black uppercase tracking-widest">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={field.name}
              type="number"
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, parseInt(e.target.value))}
              className="h-12"
            />
            {field.helpText && (
              <p className="text-[10px] font-bold text-foreground/50 uppercase italic">{`// ${field.helpText}`}</p>
            )}
          </div>
        )

      default:
        return (
          <div key={field.name} className="space-y-2">
            <Label htmlFor={field.name} className="text-[10px] font-black uppercase tracking-widest">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </Label>
            <Input
              id={field.name}
              type="text"
              placeholder={field.placeholder}
              value={value}
              onChange={(e) => handleFieldChange(field.name, e.target.value)}
              className="h-12"
            />
            {field.helpText && (
              <p className="text-[10px] font-bold text-foreground/50 uppercase italic">{`// ${field.helpText}`}</p>
            )}
          </div>
        )
    }
  }

  const renderStepContent = () => {
    if (!command.steps || command.steps.length === 0) {
      return (
        <div className="py-12 text-center">
          <Terminal className="h-12 w-12 mx-auto mb-4 text-accent" />
          <p className="font-black uppercase text-xs tracking-widest">NO_INPUT_REQUIRED</p>
          <p className="text-[10px] font-bold text-foreground/50 mt-2 uppercase tracking-tight">EXECUTE TO COMMENCE PROTOCOL</p>
        </div>
      )
    }

    const step = command.steps[currentStep]

    return (
      <div className="space-y-6">
        {step.description && (
          <div className="bg-accent/10 border-l-4 border-accent p-4">
            <p className="text-[10px] font-bold text-foreground uppercase leading-snug tracking-tight">
              {step.description.toUpperCase()}
            </p>
          </div>
        )}
        <div className="space-y-4">
          {step.fields.map(renderField)}
        </div>
      </div>
    )
  }

  const renderResult = () => {
    if (!executionResult) return null

    const isSuccess = executionResult.status === "success" || executionResult.status === "deployed"
    const Icon = isSuccess ? CheckCircle2 : XCircle

    return (
      <div className="space-y-6">
        <div className={`flex items-center gap-3 p-4 border-2 ${isSuccess ? "bg-accent/20 border-accent text-accent" : "bg-red-500/20 border-red-500 text-red-500"}`}>
          <Icon className="h-6 w-6 shrink-0" />
          <span className="font-black text-xs uppercase tracking-widest">
            {isSuccess ? "PROTOCOL_EXECUTION_SUCCESSFUL" : "PROTOCOL_EXECUTION_FAILED"}
          </span>
        </div>

        {executionResult.error && (
          <div className="p-4 bg-red-500/10 border-2 border-red-500">
            <p className="text-[10px] font-bold text-red-500 uppercase tracking-tighter italic">{`>> ERROR: ${executionResult.error.toUpperCase()}`}</p>
          </div>
        )}

        {executionResult.generated_contract_code && (
          <div className="space-y-2">
            <Label className="text-[10px] font-black uppercase">GENERATED_OUTPUT_LOG</Label>
            <ScrollArea className="h-[300px] w-full border-2 border-foreground bg-black p-4">
              <pre className="text-[10px] font-mono text-accent whitespace-pre-wrap">
                <code>{executionResult.generated_contract_code}</code>
              </pre>
            </ScrollArea>
          </div>
        )}

        <div className="grid grid-cols-1 gap-2">
          {executionResult.project_dir && (
            <div className="p-3 border-2 border-foreground bg-muted/10">
              <p className="text-[10px] font-black uppercase flex justify-between">
                <span className="opacity-50 tracking-widest">WORKSPACE_PATH</span>
                <span>{executionResult.project_dir}</span>
              </p>
            </div>
          )}

          {executionResult.transaction_id && (
            <div className="p-3 border-2 border-foreground bg-muted/10">
              <p className="text-[10px] font-black uppercase flex justify-between">
                <span className="opacity-50 tracking-widest">TX_ID</span>
                <span className="text-accent truncate ml-4">{executionResult.transaction_id}</span>
              </p>
            </div>
          )}
        </div>
      </div>
    )
  }

  const content = (
    <div className="py-4">
      {isExecuting ? (
        <div className="py-12 space-y-6">
          <div className="flex items-center justify-center">
            <div className="relative">
              <Loader2 className="h-12 w-12 animate-spin text-accent" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-4 h-4 bg-accent animate-pulse" />
              </div>
            </div>
          </div>
          <div className="text-center space-y-2">
            <p className="text-[10px] font-black uppercase tracking-[0.4em] animate-pulse">
              EXECUTING_COMMAND_LOGS
            </p>
            <p className="text-[8px] font-bold text-foreground/50 uppercase italic tracking-widest">
              INITIALIZING_FLOW_PROTOCOL_V2...
            </p>
          </div>
          <div className="h-1 bg-muted/20 border border-foreground/10 overflow-hidden max-w-xs mx-auto">
            <div className="h-full bg-accent animate-[loading_2s_ease-in-out_infinite]" style={{ width: '30%' }} />
          </div>
        </div>
      ) : executionResult ? (
        renderResult()
      ) : (
        renderStepContent()
      )}
    </div>
  )

  const footer = !executionResult && (
    <div className="flex gap-4 pt-6 border-t-2 border-foreground">
      {command.steps && command.steps.length > 1 && currentStep > 0 && (
        <Button 
          variant="outline" 
          onClick={handleBack} 
          disabled={isExecuting}
          className="flex-1 h-14 border-2 font-black uppercase text-xs"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          BACK_STEP
        </Button>
      )}
      {command.steps && currentStep < command.steps.length - 1 ? (
        <Button 
          onClick={handleNext} 
          disabled={isExecuting}
          className="flex-1 h-14 border-2 font-black uppercase text-xs"
        >
          NEXT_STEP
          <ArrowRight className="ml-2 h-4 w-4" />
        </Button>
      ) : (
        <Button 
          onClick={handleExecute} 
          disabled={isExecuting}
          className="flex-1 h-14 border-2 font-black uppercase text-xs bg-foreground text-background hover:bg-accent hover:text-black"
        >
          {isExecuting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              EXECUTING_CMD
            </>
          ) : (
            <>
              COMMENCE_EXECUTION
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      )}
    </div>
  )

  if (useSheetLayout) {
    return (
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="w-full sm:max-w-2xl bg-background border-l-4 border-foreground p-0 rounded-none overflow-y-auto">
          <div className="p-8">
            <SheetHeader className="mb-8">
              <div className="flex items-center gap-3 mb-2">
                <div className="h-10 w-10 bg-accent border-2 border-foreground flex items-center justify-center">
                  <Terminal className="h-6 w-6 text-black" />
                </div>
                <SheetTitle className="text-3xl font-black tracking-tighter uppercase leading-none">{command.name}</SheetTitle>
              </div>
              <SheetDescription className="text-xs font-bold text-foreground/80 uppercase tracking-tight border-l-4 border-accent pl-4">
                {command.description.toUpperCase()}
              </SheetDescription>
              {command.steps && command.steps.length > 1 && (
                <div className="flex items-center gap-2 pt-6">
                  {command.steps.map((_, idx) => (
                    <div
                      key={idx}
                      className={`h-2 flex-1 border border-foreground ${
                        idx <= currentStep ? "bg-accent" : "bg-muted/20"
                      }`}
                    />
                  ))}
                </div>
              )}
            </SheetHeader>
            {content}
            {footer && <div className="mt-6">{footer}</div>}
          </div>
        </SheetContent>
      </Sheet>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-background border-4 border-foreground p-8 rounded-none gap-0 overflow-hidden">
        <DialogHeader className="mb-6">
          <div className="flex items-center gap-3 mb-2">
            <div className="h-8 w-8 bg-accent border-2 border-foreground flex items-center justify-center shrink-0">
              <Terminal className="h-5 w-5 text-black" />
            </div>
            <DialogTitle className="text-2xl font-black tracking-tighter uppercase leading-none">{command.name}</DialogTitle>
          </div>
          <DialogDescription className="text-[10px] font-bold text-foreground/80 uppercase tracking-tight border-l-4 border-accent pl-4">
            {command.description.toUpperCase()}
          </DialogDescription>
        </DialogHeader>
        {content}
        {footer}
        <style jsx global>{`
          @keyframes loading {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(300%); }
          }
        `}</style>
      </DialogContent>
    </Dialog>
  )
}